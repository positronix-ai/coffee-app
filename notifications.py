import logging

import requests


def send_notifications(label: str, options: dict, logger: logging.Logger):
    if label not in ["YES", "NO", "UNSURE", "WAITING", "LOADING"]:
        logger.info(f"Unknown label: {label}")
        label = "UNSURE"

    if "stacklight" in options:
        logger.info("Sending to stacklight")
        stacklight_options = options["stacklight"]
        post_to_stacklight(label, stacklight_options)


def post_to_stacklight(label: str, options: dict):
    ip: str = options["ip"]
    port = "8080"

    # http post to stacklight
    requests.post(f"http://{ip}:{port}/display", data=label)
