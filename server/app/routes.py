from flask import jsonify
import pandas as pd

def register_routes(app):
    @app.route("/")
    def home():
        return jsonify({"message": "Backend is running."})

    @app.route("/data")
    def get_google_sheet_data():
        SHEET_ID = "your_google_sheet_id"
        SHEET_NAME = "Sheet1"
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

        try:
            df = pd.read_csv(url)
            return jsonify(df.to_dict(orient="records"))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
