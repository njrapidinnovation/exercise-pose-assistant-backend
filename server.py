import time

import cv2
import mediapipe as mp
import numpy as np
from av import VideoFrame
from flask import Flask, Response, render_template

from app.config.env_vars import HOST, PORT, TEMPLATES_FOLDER
from app.helpers.webrtc_release import process_frame

app = Flask(
    __name__,
    template_folder="app/templates",
    static_url_path="/app/static",
    static_folder="app/static",
)


@app.route("/server_video")
def server_video():
    return render_template("index_4.html")


def generate():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video capture.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        start_time = time.time()
        # Create a VideoFrame from the captured frame
        av_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        # Process the frame
        processed_frame = process_frame(av_frame)
        # Convert the processed frame to a numpy array
        image = processed_frame.to_ndarray(format="bgr24")
        end_time = time.time()

        delay_time = end_time - start_time
        fps = 1.0 / delay_time

        # Display the delay time on the frame
        cv2.putText(
            image,
            f"Delay: {delay_time:.2f} sec",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            image,
            f"FPS: {fps:.2f}",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # Encode image as jpeg
        ret, jpeg = cv2.imencode(".jpg", image)
        frame = jpeg.tobytes()

        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    cap.release()


@app.route("/video_feed_server")
def video_feed_server():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(debug=True, host=HOST, port=PORT)
