
import mediapipe as mp
import numpy as np
import math
import cv2

from av import VideoFrame

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Function to check if the body is fully covered and in the right posture


def check_body_coverage_and_posture(landmarks):
    required_landmarks = [0, 11, 12, 23, 24, 25, 26, 27, 28]
    for idx in required_landmarks:
        if landmarks[idx].visibility < 0.5:
            return False
    return True

# Function to calculate head rotation angle


def calculate_head_rotation(landmarks):
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]

    # Calculate the midpoint between the shoulders to act as a reference
    mid_shoulder_x = (right_shoulder.x + left_shoulder.x) / 2
    mid_shoulder_y = (right_shoulder.y + left_shoulder.y) / 2

    # Calculate the difference in coordinates between the nose and the shoulder midpoint
    x_diff = nose.x - mid_shoulder_x
    y_diff = nose.y - mid_shoulder_y

    # Calculate the rotation angle (in degrees)
    rotation_angle = math.degrees(math.atan2(y_diff, x_diff))

    # Normalize the angle to be within the range 0 to 180 degrees
    if rotation_angle < 0:
        rotation_angle += 360
    if rotation_angle > 180:
        rotation_angle = 360 - rotation_angle

    return rotation_angle


# Function to calculate head lean angle
def calculate_head_lean(landmarks):
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

    # Calculate the midpoint between the shoulders
    mid_shoulder_x = (left_shoulder.x + right_shoulder.x) / 2
    mid_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2

    # Calculate the vector from the midpoint to the nose
    vector_mid_to_nose = (nose.x - mid_shoulder_x, nose.y - mid_shoulder_y)

    # Determine which shoulder to use based on the direction of the lean
    if vector_mid_to_nose[0] < 0:  # Leaning left
        shoulder = left_shoulder
    else:  # Leaning right
        shoulder = right_shoulder

    # Calculate the vector from the midpoint to the chosen shoulder
    vector_mid_to_shoulder = (
        shoulder.x - mid_shoulder_x, shoulder.y - mid_shoulder_y)

    # Calculate the angle between the two vectors
    dot_product = vector_mid_to_nose[0] * vector_mid_to_shoulder[0] + \
        vector_mid_to_nose[1] * vector_mid_to_shoulder[1]
    magnitude_nose = math.sqrt(
        vector_mid_to_nose[0]**2 + vector_mid_to_nose[1]**2)
    magnitude_shoulder = math.sqrt(
        vector_mid_to_shoulder[0]**2 + vector_mid_to_shoulder[1]**2)
    angle_radians = math.acos(
        dot_product / (magnitude_nose * magnitude_shoulder))
    angle_degrees = math.degrees(angle_radians)

    # Determine the direction of the lean
    if vector_mid_to_nose[0] >= 0:  # Leaning right
        angle_degrees = 180 - angle_degrees

    return angle_degrees


# Function to get neck position
def get_neck_position(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        neck_x = int((left_shoulder.x + right_shoulder.x) * image.shape[1] / 2)
        neck_y = int((left_shoulder.y + right_shoulder.y) * image.shape[0] / 2)

        return (neck_x, neck_y)
    else:
        return None


def create_3d_rotation_arrow(image, neck_position, direction, rotation_angle):
    arrow_image = np.zeros_like(image, dtype=np.uint8)
    center = neck_position
    radius = 50  # Adjust the radius as needed to fit around the neck
    color = (0, 255, 0)
    thickness = 15
    start_angle = 0
    end_angle = 180 if direction == 'right' else 0
    if direction == 'left':
        start_angle = 180
        end_angle = 360

    # Draw the 3D arc with perspective effect
    for i in range(thickness):
        offset = i - thickness // 2
        cv2.ellipse(arrow_image, (center[0], center[1] + offset),
                    (radius, radius - 20), 0, start_angle, end_angle, color, 1)

    return arrow_image

# Function to calculate angle between three points
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return angle

# Function to calculate all angles
def calculate_all_angles(landmarks):
    angles = {}

    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    angles["Left Elbow"] = calculate_angle(left_shoulder, left_elbow, left_wrist)

    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
    angles["Right Elbow"] = calculate_angle(right_shoulder, right_elbow, right_wrist)

    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
    angles["Left Knee"] = calculate_angle(left_hip, left_knee, left_ankle)

    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
    right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
    right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
    angles["Right Knee"] = calculate_angle(right_hip, right_knee, right_ankle)

    return angles

# Function to draw angles on the image
def draw_angles(image, angles, landmarks):
    for key, value in angles.items():
        if "Left" in key:
            joint = mp_pose.PoseLandmark.LEFT_KNEE.value
        else:
            joint = mp_pose.PoseLandmark.RIGHT_KNEE.value

        joint_x = int(landmarks[joint].x * image.shape[1])
        joint_y = int(landmarks[joint].y * image.shape[0])

        cv2.putText(image, f"{value:.1f}", (joint_x - 50, joint_y - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

# Define the stages and their thresholds
all_stages = {
    "head_rotate": {
        "exercises": [
            # {
            #     "name": "check_posture",
            #     "check_function": lambda landmarks: check_body_coverage_and_posture(landmarks),
            #     "feedback": "Ensure your whole body is visible and in the correct posture.",
            #     "next_stage": "head_rotation_right",
            #     "success_feedback": "Posture correct. Proceeding to next phase."
            # },
            {
                "name": "head_rotation_right",
                "check_function": lambda landmarks: calculate_head_rotation(landmarks) < 75,
                "feedback": "Rotate your head to the right shoulder.",
                "next_stage": "head_rotation_right_to_centre",
                "success_feedback": "Good job! Now rotate your head back to the center.",
                "direction": "right"
            },
            {
                "name": "head_rotation_right_to_centre",
                "check_function": lambda landmarks: 80 < calculate_head_rotation(landmarks) < 95,
                "feedback": "Return your head to the center position.",
                "next_stage": "head_rotation_left",
                "success_feedback": "Well done! Now rotate your head to the left shoulder.",
                "direction": "left"
            },
            {
                "name": "head_rotation_left",
                "check_function": lambda landmarks: calculate_head_rotation(landmarks) >= 110,
                "feedback": "Rotate your head to the left shoulder.",
                "next_stage": "head_rotation_left_to_centre",
                "success_feedback": "Excellent! Now return your head to the center.",
                "direction": "left"
            },
            {
                "name": "head_rotation_left_to_centre",
                "check_function": lambda landmarks: 80 < calculate_head_rotation(landmarks) < 95,
                "feedback": "Return your head to the center position.",
                "next_stage": None,
                "success_feedback": "Great! You've completed the head rotation exercise.",
                "direction": "right"
            }
        ],
        "accuracy_params": {
            "min_right_rotation": 90,
            "max_left_rotation": 0
        }
    },
    "head_lean": {
        "exercises": [
            # {
            #     "name": "check_posture",
            #     "check_function": lambda landmarks: check_body_coverage_and_posture(landmarks),
            #     "feedback": "Ensure your whole body is visible and in the correct posture.",
            #     "next_stage": "head_lean_right",
            #     "success_feedback": "Posture correct. Proceeding to next phase."
            # },
            {
                "name": "head_lean_right",
                "check_function": lambda landmarks: calculate_head_lean(landmarks) < 70,
                "feedback": "Lean your head to the right shoulder.",
                "next_stage": "head_lean_centre_from_right",
                "success_feedback": "Great! Now return your head to the center.",
                "direction": "right"
            },
            {
                "name": "head_lean_centre_from_right",
                "check_function": lambda landmarks: 80 < calculate_head_lean(landmarks) < 100,
                "feedback": "Bring your head back to the center position.",
                "next_stage": "head_lean_left",
                "success_feedback": "Well done! Now lean your head to the left shoulder.",
                "direction": "left"
            },
            {
                "name": "head_lean_left",
                "check_function": lambda landmarks: calculate_head_lean(landmarks) > 110,
                "feedback": "Lean your head to the left shoulder.",
                "next_stage": "head_lean_centre_from_left",
                "success_feedback": "Excellent! Now return your head to the center.",
                "direction": "left"
            },
            {
                "name": "head_lean_centre_from_left",
                "check_function": lambda landmarks: 70 < calculate_head_lean(landmarks) < 100,
                "feedback": "Bring your head back to the center position.",
                "next_stage": None,
                "success_feedback": "Great job! You've completed the head leaning exercise.",
                "direction": "right"
            }
        ],
        "accuracy_params": {
            "min_right_leaning": 90,
            "max_left_leaning": 0
        }
    },
    "squat": {
        "exercises": [
            {
                "name": "squat_down",
                "check_function": lambda landmarks: calculate_all_angles(landmarks)["Left Knee"] < 160 and calculate_all_angles(landmarks)["Right Knee"] < 160,
                "feedback": "Lower down to squat position.",
                "next_stage": "squat_up",
                "success_feedback": "Now stand up.",
                "direction": "down"
            },
            {
                "name": "squat_up",
                "check_function": lambda landmarks: calculate_all_angles(landmarks)["Left Knee"] >= 160 and calculate_all_angles(landmarks)["Right Knee"] >= 160,
                "feedback": "Stand up straight.",
                "next_stage": None,
                "success_feedback": "Great job! You've completed the squat exercise.",
                "direction": "up"
            }
        ],
        "accuracy_params": {
            "min_squat_angle": 60,
            "max_stand_angle": 160
        }
    }
}



def process_frame(frame, exercise_start_index, current_stage):
    stages_key_list = list(all_stages.keys())
    current_exercise_stages = all_stages[stages_key_list[exercise_start_index]]["exercises"]

    print("Process Frames-->", exercise_start_index, current_stage)
    if not current_stage:
        current_stage = current_exercise_stages[0]["name"]

    feedback = ""

    image = frame.to_ndarray(format='bgr24')
    image = cv2.flip(image, 1)

    # Convert the BGR image to RGB before processing.
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        landmarks = results.pose_landmarks.landmark

        # rotation_angle = calculate_head_rotation(landmarks)

        for stage in current_exercise_stages:
            if stage["name"] == current_stage:
                if stage["check_function"](landmarks):
                    feedback = stage["success_feedback"]
                    current_stage = stage["next_stage"]
                else:
                    # If the condition is not met, provide feedback and remain in the same stage
                    feedback = stage["feedback"]
                    feedback = f"{feedback}"

                # # Create and display a rotating 3D arrow image if required
                # if "direction" in stage:
                #     neck_position = get_neck_position(image=image)
                #     if neck_position:
                #         rotation_arrow = create_3d_rotation_arrow(
                #             image, neck_position, stage["direction"], rotation_angle)
                #         image = cv2.addWeighted(
                #             image, 1, rotation_arrow, 0.5, 0)
                # break

        # # Display feedback on the image
        # cv2.putText(image, feedback, (10, 70),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)

    # Rebuild a VideoFrame, preserving timing information
    new_frame = VideoFrame.from_ndarray(image, format="bgr24")
    new_frame.pts = frame.pts
    new_frame.time_base = frame.time_base
    return new_frame, current_stage, feedback
