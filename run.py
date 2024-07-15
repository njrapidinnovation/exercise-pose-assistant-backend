import asyncio

from aiohttp import web

from app import create_app as create_flask_app
from app import webrtc_app
from app.config.config import get_config
from app.controllers.aiohttp_2 import (
    index_new,
    javascript_new,
    stop_new,
    video_feed_new,
)
from app.controllers.release import index, javascript, offer, on_shutdown

args, ssl_context = get_config()
web_app = webrtc_app()
flask_app = create_flask_app()


async def main():
    args, ssl_context = get_config()

    # Setup aiohttp web application
    web_app.router.add_get("/video", index_new)
    web_app.router.add_get("/client_2.js", javascript_new)
    web_app.router.add_get("/video_feed_new", video_feed_new)
    web_app.router.add_get("/stop_new", stop_new)

    # Create aiohttp web runner
    runner = web.AppRunner(web_app)
    await runner.setup()

    # Create aiohttp TCP site
    site = web.TCPSite(runner, args.host, args.port, ssl_context=ssl_context)
    await site.start()

    try:
        await asyncio.sleep(3600)  # Serve indefinitely until terminated
    except KeyboardInterrupt:
        pass
    finally:
        await runner.cleanup()


def create_aiohttp_app(app):
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)
    return app


if __name__ == "__main__":

    web_app = create_aiohttp_app(web_app)
    asyncio.run(main())
    web.run_app(web_app, host=args.host, port=args.port, ssl_context=ssl_context)
