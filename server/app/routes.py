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
        KEY_PATH = os.path.join("scalingsociety-0198f5b3d2d5.json")

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

    
