from aiohttp import web
from flask import Flask


def create_app():

    # Register blueprintsdef create_app()
    app = Flask(__name__, static_folder="static", template_folder="templates")

    return app


def webrtc_app():

    web_app = web.Application()
    return web_app
