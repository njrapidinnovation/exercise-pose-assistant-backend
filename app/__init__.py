from aiohttp import web
from flask import Flask
from flask_cors import CORS


def create_app():

    # Register blueprintsdef create_app()
    app = Flask(__name__, static_folder="static", template_folder="templates")
    CORS(app)  # Allow CORS for all domains.

    return app