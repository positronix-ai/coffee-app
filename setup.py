# Outline of what an app wants to know from glruntime
# API token is assumed to be in the environment variable GROUNDLIGHT_API_TOKEN
from typing import List
from framegrab import FrameGrabber
from groundlight import Groundlight

def get_cameras() -> List[FrameGrabber]: # TODO define a camera type
    config = {
        'input_type': 'generic_usb',
    }
    grabber = FrameGrabber.create_grabber(config)
    return [grabber]

def get_detectors() -> List: # TODO should be a Groundlight detector, waiting for exposed change in sdk
    gl = Groundlight()
    det = gl.get_or_create_detector("coffee_detector", "Is the coffee filter (the gray circle) free of coffee grounds?")
    return [det]