from flask import jsonify
import pandas as pd
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def register_routes(app):
    @app.route("/")
    def home():
        return jsonify({"message": "Backend is running."})

    @app.route("/data")
    def get_google_sheet_data():
        # 1) Sheet and credential settings
        SHEET_ID = "1u_RbVYhuedUIVsPVMQMuKxYP05o-95TYWWK0NqvrhyU"
        SHEET_NAME = "Form Responses 1"
        RANGE = f"{SHEET_NAME}!A1:K"  # columns A through K

        # Path to your service account JSON
        KEY_PATH = os.path.join("scalingsociety-0198f5b3d2d5.json")

        # 2) Load service account credentials
        creds = service_account.Credentials.from_service_account_file(
            KEY_PATH,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )

        # 3) Build the Sheets API client
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        try:
            # 4) Fetch the values
            result = sheet.values().get(
                spreadsheetId=SHEET_ID,
                range=RANGE
            ).execute()
            values = result.get("values", [])

            # 5) Convert to DataFrame (first row = header)
            if not values:
                return jsonify([])  # empty list if no data

            df = pd.DataFrame(values[1:], columns=values[0])

            # 6) Return as JSON
            return jsonify(df.to_dict(orient="records"))

        except Exception as e:
            return jsonify({"error": str(e)}), 500
