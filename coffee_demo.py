import logging
import threading
import time
import traceback
from collections import deque
from typing import Union

import numpy as np
from framegrab import FrameGrabber
from groundlight import Groundlight
from groundlight.internalapi import ImageQuery
from openapi_client.exceptions import ForbiddenException

from notifications import send_notifications

####################################################################################################
# Groundlight demo app to trigger a notification when the coffee machine is not rinsed after use
# set GROUNDLIGHT_API_TOKEN to your API token in the environment
####################################################################################################

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# Should be configured to use the edge endpoint
gl = Groundlight()  # API key should be in environment variable

notification_options = {
    "stacklight": {"ip": "10.44.3.69", "password": "", "ssid": ""},
}

# Target detector ID for coffee demo
TARGET_DETECTOR = "det_2U80DZ4lmJITkEJCfzlQOGu8SaS"


class PrefetchingVideoCapture:
    """A class to capture frames from a camera in a separate thread."""

    def __init__(self):
        # Setup camera
        config = {
            "input_type": "generic_usb",
        }
        self.grabber = FrameGrabber.create_grabber(config)
        self.frame = None
        self.frame_id = -1  # Initialize a frame identifier
        self.last_processed_id = -1  # Keep track of the last processed frame
        self.read_lock = threading.Lock()
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self) -> None:
        """Update the current frame in a thread-safe manner."""
        while True:
            frame: np.ndarray = self.grabber.grab()  # slow step; ~90ms
            with self.read_lock:
                self.frame = frame
                self.frame_id += 1  # Increment frame identifier

    def read(self) -> Union[None, np.ndarray]:
        """Read the current frame in a thread-safe manner."""
        with self.read_lock:
            if self.frame is None or self.frame_id == self.last_processed_id:
                return None  # Return None if no new frame is available
            self.last_processed_id = self.frame_id  # Update last processed frame ID
            return self.frame.copy()

    def capture(self) -> Union[None, np.ndarray]:
        """Poll the camera until a frame is available."""
        try:
            img = None
            while True:
                img = self.read()  # Returns a numpy BGR image from cv2
                if img is not None:
                    break
                time.sleep(0.05)
        except Exception:  # pylint: disable=broad-except
            traceback.print_exc()
            logger.error("failed to capture image")
            img = None
        return img

    def release(self) -> None:
        """Release the camera."""
        self.grabber.release()


def map_result(iq, threshold: float) -> str:
    """
    Interprets the result of an image query and returns a string representing
    the answer, or "UNSURE" if the confidence is below the threshold.
    """
    if not iq.result:
        answer = "UNSURE"
    if (iq.result.confidence is not None) and (iq.result.confidence < threshold):
        answer = "UNSURE"
    else:
        answer = iq.result.label
    return answer


def confident_image_query(detector_id: str, image: np.ndarray, threshold=0.75, timeout=3.0) -> tuple[str | None, str]:
    """query detector and wait for confidence above threshold, return None on problem"""
    start_time = time.time()
    try:
        iq: ImageQuery = gl.ask_ml(detector_id, image, wait=timeout)
    except ForbiddenException:
        # Return "LOADING" to cause the stacklight to flash yellow
        return "LOADING", "Are there Grounds?: ERROR 403 Forbidden (check API token)"
    except Exception as ex:  # pylint: disable=broad-except
        traceback.print_exc()
        time.sleep(3)  # make sure we don't get stuck in a fast loop
        return "LOADING", f"Are there Grounds?: ERROR {ex}"

    elapsed = time.time() - start_time

    answered_on = "CLOUD" if iq.id.startswith("iq_") else "EDGE "
    label = map_result(iq, threshold)
    if not iq.result:
        message = f"Are there Grounds?: '{label}'\t{answered_on} NO RESULT after {elapsed:.2f}s"
    if iq.result.confidence is None:  # Very unlikely w/ short timeout
        message = f"Are there Grounds?: '{label}'\t{answered_on} HUMAN ANSWERED after {elapsed:.2f}s  (HUMAN% > {threshold * 100}%)"
    elif iq.result.confidence >= threshold:
        message = f"Are there Grounds?: '{label}'\t{answered_on} ML CONFIDENT after {elapsed:.2f}s   ({(iq.result.confidence * 100):.1f}% > {threshold * 100}%)"
    else:
        message = f"Are there Grounds?: '{label}'\t{answered_on} NOT CONFIDENT after {elapsed:.2f}s  ({(iq.result.confidence * 100):.1f}% < {threshold * 100}%)"
    message += " TIMEOUT!" if elapsed >= timeout else ""

    return label, message


def main():
    """Main loop for sending images to the edge-endpoint and processing the results."""
    # Setup camera
    cap = PrefetchingVideoCapture()
    iter_speeds = deque(maxlen=100)

    previous_result = None
    start_time = time.time()
    renotify_time = time.time()
    while True:
        img = cap.capture()
        if img is None:
            logger.warning("failed to capture image, sleeping")
            time.sleep(0.5)
            continue

        result, message = confident_image_query(detector_id=TARGET_DETECTOR, image=img, threshold=0.75)

        # Instantly use the stacklight alert
        if previous_result != result or time.time() - renotify_time > 30:
            try:
                send_notifications(label=result, options=notification_options, logger=logger)
                renotify_time = time.time()
            except Exception as ex:  # pylint: disable=broad-except
                print(f"Error sending notification to stacklight: {ex}")

        previous_result = result

        # Compute FPS over the last 100 frames
        end_time = time.time()
        iter_time = end_time - start_time
        iter_speeds.append(iter_time)
        avg_iter_speed = sum(iter_speeds) / len(iter_speeds)
        fps = 1 / avg_iter_speed
        start_time = end_time

        print(f"{message}  [{fps:.2f} frames/s]")


if __name__ == "__main__":
    main()
