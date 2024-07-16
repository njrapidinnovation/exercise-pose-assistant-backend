import asyncio
import warnings

import cv2
from aiohttp import web
from av import VideoFrame

from app import create_app as create_flask_app
from app import webrtc_app
from app.config.config import get_config
from app.helpers.webrtc_release import process_frame

warnings.filterwarnings("ignore", category=DeprecationWarning)


stop_event = asyncio.Event()  # Event to signal stop


# async def video_feed_new(request):

#     stop_event.clear()  # Clear the stop event when starting the video feed

#     async def video_stream():
#         cap = cv2.VideoCapture(0)
#         if not cap.isOpened():
#             print("Error: Could not open video capture.")
#             return

#         try:
#             while cap.isOpened():
#                 if stop_event.is_set():
#                     break

#                 ret, frame = cap.read()
#                 if not ret:
#                     break

#                 # Process the frame
#                 av_frame = VideoFrame.from_ndarray(frame, format="bgr24")
#                 processed_frame = process_frame(av_frame)
#                 image = processed_frame.to_ndarray(format="bgr24")

#                 # Encode image to JPEG
#                 ret, jpeg = cv2.imencode(".jpg", image)
#                 if not ret:
#                     continue

#                 # Convert JPEG to bytes
#                 frame_bytes = jpeg.tobytes()

#                 # Yield frame bytes as multipart content
#                 yield (
#                     b"--frame\r\n"
#                     b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
#                 )
#                 await asyncio.sleep(0.01)  # Allow other tasks to run
#         finally:
#             cap.release()

#     return web.Response(
#         headers={"Content-Type": "multipart/x-mixed-replace; boundary=frame"},
#         body=video_stream(),
#     )


async def video_feed_new(request):
    print("called video feed")
    stop_event.clear()  # Clear the stop event when starting the video feed

    async def video_stream():
        print("Video stream called")
        cap = cv2.VideoCapture("/dev/video0")
        # video_path = "output.mov"

        # cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error: Could not open video capture.")
            return

        try:
            while cap.isOpened():
                if stop_event.is_set():
                    break

                ret, frame = cap.read()
                if not ret:
                    break

                # Process the frame
                av_frame = VideoFrame.from_ndarray(frame, format="bgr24")
                processed_frame = process_frame(av_frame)
                image = processed_frame.to_ndarray(format="bgr24")

                # Encode image to JPEG
                ret, jpeg = cv2.imencode(".jpg", image)
                if not ret:
                    continue

                # Convert JPEG to bytes
                frame_bytes = jpeg.tobytes()

                # Yield frame bytes as multipart content
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )
                await asyncio.sleep(0.01)  # Allow other tasks to run
        finally:
            cap.release()

    response = web.StreamResponse(
        headers={"Content-Type": "multipart/x-mixed-replace; boundary=frame"}
    )
    await response.prepare(request)
    async for frame in video_stream():
        await response.write(frame)
    return response


async def stop_new(request):
    print("stop called")
    stop_event.set()
    return web.Response(text="Webcam stopped.")


async def index_new(request):
    content = open("app/templates/index_2.html", "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript_new(request):
    content = open("app/static/client_2.js", "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def shutdown(server, app):
    # Cleanup tasks before shutdown (if any)
    await server.shutdown()
    await app.shutdown()


# async def main():
#     # Initialize your Flask app or any other setup needed
#     args, ssl_context = get_config()
#     flask_app = create_flask_app()

#     # Setup aiohttp web application
#     app = web.Application()
#     app.router.add_get("/", index)
#     app.router.add_get("/client.js", javascript)
#     app.router.add_get("/video_feed", video_feed)
#     app.router.add_get("/stop", stop)
#     app.router.add_get("/stop_new", stop_new)

#     # Create aiohttp web runner
#     runner = web.AppRunner(app)
#     await runner.setup()

#     # Create aiohttp TCP site
#     site = web.TCPSite(runner, args.host, args.port, ssl_context=ssl_context)
#     await site.start()

#     try:
#         await asyncio.sleep(3600)  # Serve indefinitely until terminated
#     except KeyboardInterrupt:
#         pass
#     finally:
#         await runner.cleanup()


# if __name__ == "__main__":
#     asyncio.run(main())


# async def main():
#     args, ssl_context = get_config()

#     # Setup aiohttp web application
#     aiohttp_app = webrtc_app()
#     aiohttp_app.router.add_get("/video", index_new)
#     aiohttp_app.router.add_get("/client_2.js", javascript_new)
#     aiohttp_app.router.add_get("/video_feed_new", video_feed_new)
#     aiohttp_app.router.add_get("/stop_new", stop_new)

#     # Create aiohttp web runner
#     runner = web.AppRunner(aiohttp_app)
#     await runner.setup()

#     # Create aiohttp TCP site
#     site = web.TCPSite(runner, args.host, args.port, ssl_context=ssl_context)
#     await site.start()

#     try:
#         await asyncio.sleep(3600)  # Serve indefinitely until terminated
#     except KeyboardInterrupt:
#         pass
#     finally:
#         await runner.cleanup()


# class ToRun:
#     def __init__(self) -> None:
#         asyncio.run(main())
