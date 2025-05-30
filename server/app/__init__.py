from flask import Flask
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    
    # Register routes
    register_routes(app)

    return app