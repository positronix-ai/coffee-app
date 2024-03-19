import time
from imgcat import imgcat
from framegrab import FrameGrabber


if __name__ == "__main__":
    config = {
        'input_type': 'generic_usb',
    }
    grabber = FrameGrabber.create_grabber(config)

    while True:
        print("Capturing frame: {}".format(time.time()))
        frame = grabber.grab()
        imgcat(frame)
        time.sleep(3)
