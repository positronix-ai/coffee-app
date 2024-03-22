import logging
import threading
import time
from time import sleep
import traceback
from collections import deque
from typing import Union

import numpy as np
from framegrab import FrameGrabber
from groundlight import Groundlight
from groundlight.internalapi import ImageQuery
from openapi_client.exceptions import ForbiddenException

from setup import get_cameras, get_detectors

####################################################################################################
# Groundlight demo app to trigger a notification when the coffee machine is not rinsed after use
# set GROUNDLIGHT_API_TOKEN to your API token in the environment
####################################################################################################

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# Should be configured to use the edge endpoint
gl = Groundlight()  # API key should be in environment variable

def main():
    """Main loop for sending images to the edge-endpoint and processing the results."""
    # Setup camera
    det = get_detectors()[0]
    cam = get_cameras()[0]

    while True:
        frame = cam.grab()
        result = gl.ask_ml(det, frame)
        sleep(60)
        # notifications can be configured manually in the Groundlight web interface

if __name__ == "__main__":
    main()
