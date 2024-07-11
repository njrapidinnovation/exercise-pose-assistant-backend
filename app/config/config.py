import argparse
import logging
import ssl

from .env_vars import HOST, PORT, ROOT, SECRET_KEY, STATIC_FOLDER, TEMPLATES_FOLDER


class Config:

    SECRET_KEY: str = SECRET_KEY
    TEMPLATES_FOLDER: str = TEMPLATES_FOLDER
    ROOT: str = ROOT
    STATIC_FOLDER: str = STATIC_FOLDER
    HOST: str = HOST
    PORT: int = PORT


def get_config():
    parser = argparse.ArgumentParser(
        description="WebRTC audio / video / data-channels demo"
    )
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--host", default=HOST, help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=PORT, help="Port for HTTP server (default: 5000)"
    )
    parser.add_argument("--record-to", help="Write received media to a file.")
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.cert_file and args.key_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    return args, ssl_context
