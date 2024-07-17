import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define Folder path
ROOT = os.path.dirname(__file__)
BASE_DIR: str = os.path.abspath(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)

# Create path to email template directory
DEMO_VIDEO_PATH: str = os.path.join(BASE_DIR, "demo-instruct.wav")


STATIC_FOLDER = "app/static"
TEMPLATES_FOLDER = "app/templates"


# Define environment
ENV_TYPE = os.environ.get("ENV", "local")

# Define configuration variables
HOST: str = os.environ["HOST"]
PORT = int(os.environ["PORT"])
SECRET_KEY: str = os.environ["SECRET_KEY"]

# get socket url
SOCKET_URL_LOCAL = f"http://{HOST}:{PORT}"
SOCKET_URL_SERVER = f"https://{HOST}:{PORT}"
