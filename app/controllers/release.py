# import argparse
# import asyncio
# import json
# import logging
# import os
# import ssl
# import uuid

# import cv2
# from aiohttp import web
# from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
# from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
# from av import VideoFrame
# from flask import Blueprint, current_app, jsonify, request, send_from_directory

# from app.config.env_vars import DEMO_VIDEO_PATH
# from app.helpers.webrtc_release import VideoTransformTrack, process_frame

# main = Blueprint("main", __name__)
# logger = logging.getLogger("pc")
# pcs = set()
# relay = MediaRelay()


# @main.route("/test")
# def test():
#     return "success"


# @main.route("/")
# def index():
#     return send_from_directory(current_app.static_folder, "index.html")


# @main.route("/client.js")
# def javascript():
#     return send_from_directory(current_app.static_folder, "client.js")


# @main.route("/offer", methods=["POST"])
# async def offer():
#     params = request.json  # Access request.json synchronously
#     offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

#     pc = RTCPeerConnection()
#     pc_id = "PeerConnection(%s)" % uuid.uuid4()
#     pcs.add(pc)

#     def log_info(msg, *args):
#         logger.info(pc_id + " " + msg, *args)

#     log_info("Created for1 %s", request.remote_addr)

#     # prepare local media
#     player = MediaPlayer(DEMO_VIDEO_PATH)
#     if "record_to" in request.args:
#         recorder = MediaRecorder(request.args["record_to"])
#     else:
#         recorder = MediaBlackhole()

#     @pc.on("datachannel")
#     def on_datachannel(channel):
#         @channel.on("message")
#         def on_message(message):
#             if isinstance(message, str) and message.startswith("ping"):
#                 channel.send("pong" + message[4:])

#     @pc.on("connectionstatechange")
#     async def on_connectionstatechange():
#         log_info("Connection state is %s", pc.connectionState)
#         if pc.connectionState == "failed":
#             await pc.close()
#             pcs.discard(pc)

#     @pc.on("track")
#     def on_track(track):
#         log_info("Track %s received2", track.kind)

#         if track.kind == "audio":
#             pc.addTrack(player.audio)
#             recorder.addTrack(track)
#         elif track.kind == "video":
#             pc.addTrack(
#                 VideoTransformTrack(
#                     relay.subscribe(track), transform=params["video_transform"]
#                 )
#             )
#             if "record_to" in request.args:
#                 recorder.addTrack(relay.subscribe(track))

#         @track.on("ended")
#         async def on_ended():
#             log_info("Track %s ended", track.kind)
#             await recorder.stop()

#     # handle offer
#     await pc.setRemoteDescription(offer)
#     await recorder.start()

#     # send answer
#     answer = await pc.createAnswer()
#     await pc.setLocalDescription(answer)

#     return jsonify({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})


# @main.route("/shutdown", methods=["POST"])
# async def on_shutdown():
#     # close peer connections
#     coros = [pc.close() for pc in pcs]
#     await asyncio.gather(*coros)
#     pcs.clear()
#     return "", 204
