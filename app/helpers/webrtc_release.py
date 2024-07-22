import cv2
import mediapipe as mp
import numpy as np
from aiortc import MediaStreamTrack
from av import VideoFrame
GREEN_COLOUR=(0, 255, 0)
BLUE_COLOUR=(255,0,0)
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
)
mp_drawing = mp.solutions.drawing_utils

class PoseEllipses:
    def __init__(self):
        self.initialized = False
        self.center_left = None
        self.center_right = None

def rotate_point(point, angle, center):
    angle_rad = np.deg2rad(angle)
    ox, oy = center
    px, py = point

    qx = ox + np.cos(angle_rad) * (px - ox) - np.sin(angle_rad) * (py - oy)
    qy = oy + np.sin(angle_rad) * (px - ox) + np.cos(angle_rad) * (py - oy)
    return qx, qy

def is_point_in_ellipse(point, center, axes):
    px, py = point
    cx, cy = center
    a, b = axes

    return ((px - cx) ** 2 / a**2 + (py - cy) ** 2 / b**2) <= 1

def calculate_distance(left_point, right_point,image_width,image_height):
    left_point_x=left_point.x*image_width
    left_point_y=left_point.y*image_height
    right_point_x=right_point.x*image_width
    right_point_y=right_point.y*image_height
    point1=np.array((left_point_x,left_point_y))
    point2=np.array((right_point_x,right_point_y))
    return np.linalg.norm(point1 - point2)

def process_frame(frame):
    pose_ellipses = PoseEllipses()
    img = frame.to_ndarray(format='bgr24')
    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)
    results_hand = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        right_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        image_height, image_width, _ = image.shape

        if not pose_ellipses.initialized:
            initial_left_hip_coords = (int(left_hip.x * image_width), int(left_hip.y * image_height))
            initial_right_hip_coords = (int(right_hip.x * image_width), int(right_hip.y * image_height))
            pose_ellipses.center_left = (initial_left_hip_coords[0] + 10, initial_left_hip_coords[1] - 35)
            pose_ellipses.center_right = (initial_right_hip_coords[0] - 10, initial_right_hip_coords[1] - 35)
            pose_ellipses.initialized = True

        center_left = pose_ellipses.center_left
        center_right = pose_ellipses.center_right
        ## Calculating the distance between the hip points to determine the waist size
        distance_between_the_hip_points=calculate_distance(left_hip,right_hip,image_width,image_height)
        distance_between_the_hip_and_shoulder_points_left=calculate_distance(left_hip, right_shoulder,image_width,image_height)
        
        minor_axis=int((distance_between_the_hip_points/8))
        major_axis=int((distance_between_the_hip_and_shoulder_points_left/8))
        
        area=(major_axis,minor_axis)
        rotate_left = 55
        rotate_right = 115

        cv2.ellipse(image, center_left, area, rotate_left, 0, 360, BLUE_COLOUR, -1)
        cv2.ellipse(image, center_right, area, rotate_right, 0, 360, BLUE_COLOUR, -1)
        
        if results_hand.multi_hand_landmarks:
            for hand_landmarks in results_hand.multi_hand_landmarks:
                hand_points = [
                    (int(lm.x * image.shape[1]), int(lm.y * image.shape[0]))
                    for lm in hand_landmarks.landmark
                ]
                rotated_points_left = [
                    rotate_point(pt, -rotate_left, center_left) for pt in hand_points
                ]
                rotated_points_right = [
                    rotate_point(pt, -rotate_right, center_right) for pt in hand_points
                ]

                for pt_left, pt_right in zip(rotated_points_left, rotated_points_right):
                    if is_point_in_ellipse(pt_right, center_right, area):
                        cv2.ellipse(image, center_right, area, rotate_right, 0, 360, GREEN_COLOUR, -1)
                        cv2.putText(
                            image,
                            "Hand inside right ellipse",
                            (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (255, 0, 255),
                            2,
                        )
                        break
                    elif is_point_in_ellipse(pt_left, center_left, area):
                        cv2.ellipse(image, center_left, area, rotate_left, 0, 360, GREEN_COLOUR, -1)
                        cv2.putText(
                            image,
                            "Hand inside left ellipse",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (255, 0, 255),
                            2,
                        )
                        break
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

    # Rebuild a VideoFrame, preserving timing information
    new_frame = VideoFrame.from_ndarray(image, format="bgr24")
    new_frame.pts = frame.pts
    new_frame.time_base = frame.time_base
    return new_frame


