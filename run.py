import base64
from io import BytesIO

import cv2
from av import VideoFrame
from flask_socketio import SocketIO, emit
from PIL import Image

from app import create_app as flask_create_app
from app.config.env_vars import HOST, PORT
from app.helpers.webrtc_release import process_frame

flask_app = flask_create_app()
socketio = SocketIO(flask_app, cors_allowed_origins="*")


class StreamingState:
    def __init__(self):
        self.streaming = False


streaming_state = StreamingState()


@socketio.on("frame")
def handle_frame(data):
    if not streaming_state.streaming:
        return
    try:

        image_data = base64.b64decode(data.split(",")[1])
        image = Image.open(BytesIO(image_data))
        frame = VideoFrame.from_image(image)
        processed_frame = process_frame(frame)
        _, buffer = cv2.imencode(".jpg", processed_frame.to_ndarray(format="bgr24"))
        processed_image = base64.b64encode(buffer).decode("utf-8")
        emit("processed_frame", processed_image)
    except Exception as e:
        print(f"Error processing frame: {e}")


@socketio.on("start_stream")
def handle_start_stream():
    streaming_state.streaming = True
    print("Streaming started")


@socketio.on("stop_stream")
def handle_stop_stream():
    streaming_state.streaming = False
    print("Streaming stopped")
    return
    emit("stop_stream")
    return


if __name__ == "__main__":
    socketio.run(flask_app, host=HOST, port=PORT, debug=True)
