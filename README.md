# spider-release-zone-ai

# Hand and Pose Detection using Mediapipe

This project demonstrates real-time hand and pose detection using Mediapipe. It captures video from the webcam, processes the frames to detect hands and poses, and highlights regions of interest.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/shalu-rapid/aletha_model_mediapipe.git
    cd aletha_model_mediapipe/utilities
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Ensure you have the necessary dependencies installed. If you don't have `mediapipe` and `opencv-python` installed, you can install them using:
    ```sh
    pip install mediapipe opencv-python
    ```

## Usage

To run the hand and pose detection script, use the following command:
```sh
python releaseZone.py
```

The script will open a window showing the video feed from your webcam with detected hand landmarks and pose landmarks. It also highlights the regions between the iliacus and psoas muscles and indicates if a hand is inside those regions.
