from flask import Flask
from .routes import register_routes
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    CORS(app, resources={r"/*": {"origins": frontend_url}})
    
    register_routes(app)

    return app