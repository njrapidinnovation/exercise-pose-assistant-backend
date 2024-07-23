import asyncio
import base64
import json
import time
import traceback
from fractions import Fraction
from io import BytesIO

import cv2
import websockets
from av import VideoFrame
from PIL import Image

from app.config.env_vars import HOST, SOCKET_PORT
from app.helpers.pose_feedback import process_frame

streaming_state = {"streaming": False}


async def handle_frame(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        if data["type"] == "start_stream":
            streaming_state["streaming"] = True
            await websocket.send(
                json.dumps({"type": "status", "message": "Streaming started"})
            )
        elif data["type"] == "stop_stream":
            streaming_state["streaming"] = False
            await websocket.send(
                json.dumps({"type": "status", "message": "Streaming stopped"})
            )
        elif data["type"] == "frame" and streaming_state["streaming"]:
            try:
                image_data = base64.b64decode(data["data"])
                image = Image.open(BytesIO(image_data))
                frame = VideoFrame.from_image(image)
                new_timestamp = int(time.time() * 1000000)
                frame.pts = new_timestamp
                frame.time_base = Fraction(1, 1000000)

                exercise_start_index = data.get("exercise_start_index")
                current_stage = data.get("current_stage")

                processed_frame, current_stage, feedback = process_frame(frame, exercise_start_index, current_stage)
                
                # processed_frame = frame
                _, buffer = cv2.imencode(
                    ".jpg", processed_frame.to_ndarray(format="bgr24")
                )
                processed_image = base64.b64encode(buffer).decode("utf-8")

                await websocket.send(
                    json.dumps({
                        "type": "processed_frame",
                        "data": processed_image,
                        "current_stage": current_stage,
                        "feedback": feedback
                    })
                )
            except Exception as e:
                print(f"Error processing frame: {str(e)}")
                traceback.print_exc()
                await websocket.send(
                    json.dumps(
                        {
                            "type": "error",
                            "message": f"Error processing frame: {str(e)}",
                        }
                    )
                )


async def main():
    server = await websockets.serve(
        handle_frame,
        HOST,  # Listen on all available interfaces
        SOCKET_PORT,
        ping_interval=None,
        ping_timeout=None,
        close_timeout=None,
        max_size=None,
        max_queue=None,
        read_limit=2**20,
        write_limit=2**20,
        # Add this to allow connections from any origin
        origins=None,
    )
    print("WebSocket server started on ws://0.0.0.0:8765")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
