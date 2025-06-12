from flask import jsonify
import pandas as pd
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import json

import firebase_admin
from firebase_admin import credentials, auth, firestore
from flask import abort, jsonify, request
from datetime import datetime

cred = credentials.Certificate("keys/scalingsociety-b3b3b-firebase-adminsdk-fbsvc-8f641d194f.json")
firebase_admin.initialize_app(cred)

db = firestore.client()    

INVITES = "invites"
ROLE    = "internal"

def _is_admin(token: str) -> bool:
    try:
        decoded = auth.verify_id_token(token)
        return decoded.get("admin") == True
    except Exception:
        return False

def _is_internal(token: str) -> bool:
    try:
        decoded = auth.verify_id_token(token)
        return decoded.get("role") == "internal"
    except Exception as err:
        return False

def register_routes(app):
    @app.route("/")
    def home():
        return jsonify({"message": "Backend is running."})

    @app.route("/invite", methods=["POST"])
    def invite_user():
        # 0. Require bearer token from admin dashboard
        id_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not _is_admin(id_token):
            return jsonify({"error": "Permission denied"}), 403

        # 1. Normalise e-mail
        email = (request.json.get("email") or "").strip().lower()
        if not email:
            return jsonify({"error": "Missing email"}), 400

        # 2. Check Firestore allow-list
        doc_ref = db.document(f"{INVITES}/{email}")
        doc     = doc_ref.get()

        if not doc.exists or doc.get("status") != "approved":
            return jsonify({"error": "Email not approved"}), 412

        # 3. Create / fetch Auth user
        try:
            user = auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            user = auth.create_user(email=email)

        # 4. Attach custom claim
        auth.set_custom_user_claims(user.uid, { "role": ROLE })

        # 5. Generate password-reset link
        api_key = os.getenv("FIREBASE_API_KEY")
        if not api_key:
            return jsonify({"error": "Server not configured properly"}), 500

        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }
        resp = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}",
            headers={ "Content-Type": "application/json" },
            data=json.dumps(payload),
            timeout=10
        )
        if not resp.ok:
            abort(resp.status_code, f"sendOobCode error: {resp.text}")

        # 7. Update Firestore
        doc_ref.update({
            "status": "link-sent",
            "sentAt": firestore.SERVER_TIMESTAMP,
        })

        return jsonify({ "ok": True })

    @app.route("/data")
    def get_google_sheet_data():
        if not _is_internal(request.headers.get("Authorization", "").replace("Bearer ", "")):
            print("permission-denied not internal")
            return jsonify({"error", "Permission denied"}), 403

        # Configuration for all sheets to be fetched.
        # This structure makes it easy to add more sheets in the future.
        sheets_config = [
            {
                "id": "1u_RbVYhuedUIVsPVMQMuKxYP05o-95TYWWK0NqvrhyU",
                "name": "Form Responses 1",
                "range": "A1:K",
            },
            {
                "id": "1TErh-XcN4NWyXAIO10YFMfPYjHagHHG5pNUOyCbm3U8",
                "name": "Direct application (Youtube)",
                "range": "A1:AC",
            },
            {
                "id": "1TErh-XcN4NWyXAIO10YFMfPYjHagHHG5pNUOyCbm3U8",
                "name": "Free training applicants (Youtube)",
                "range": "A1:AC",
            },
        ]

        # Path to your service account JSON
        KEY_PATH = os.path.join("keys/scalingsociety-0198f5b3d2d5.json")

        # Load service account credentials
        creds = service_account.Credentials.from_service_account_file(
            KEY_PATH,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )

        # Build the Sheets API client
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        all_sheets_data = []
        try:
            for config in sheets_config:
                # Fetch the values for the current sheet
                range_name = f"{config['name']}!{config['range']}"
                result = (
                    sheet.values()
                    .get(spreadsheetId=config["id"], range=range_name)
                    .execute()
                )
                values = result.get("values", [])

                # Convert to DataFrame (first row = header)
                if not values:
                    all_sheets_data.append([])
                    continue

                df = pd.DataFrame(values[1:], columns=values[0])
                all_sheets_data.append(df.to_dict(orient="records"))

            # Return a list of lists, where each inner list contains data from one sheet
            return jsonify(all_sheets_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    