import time

import cv2
import mss
import numpy

with mss.mss() as sct:
    monitor = {"top"}