import time

import cv2
import mss
import numpy as np
import scipy.signal

max_shift = 30

def cross_image(im1, im2):
   # get rid of the color channels by performing a grayscale transform
   # the type cast into 'float' is to avoid overflows
   im1_gray = np.sum(im1.astype('float'), axis=2)
   im2_gray = np.sum(im2.astype('float'), axis=2)

   # get rid of the averages, otherwise the results are not good
   im1_gray -= np.mean(im1_gray)
   im2_gray -= np.mean(im2_gray)

   # calculate the correlation image; note the flipping of onw of the images
   return scipy.signal.fftconvolve(im1_gray, im2_gray[::-1,::-1], mode='same')

with mss.mss() as sct:
    # Part of the screen to capture
    monitor = {"top": 100, "left": 0, "width": 800, "height": 600}

    last_frame = np.array(sct.grab(monitor))[:, :, :3]
    last_time = time.time()
    fps = 0.0
    frame_count = 0

    while "Screen capturing":
        # Get raw pixels from the screen, save it to a numpy array
        current_frame = np.array(sct.grab(monitor))[:, :, :3]
        (H, W) = current_frame.shape[:2]
        frame = cv2.UMat(current_frame)

        current_frame = current_frame[100:200, 100:200]

        self_corr = cross_image(last_frame, last_frame)
        sx, sy = np.unravel_index(np.argmax(self_corr), self_corr.shape)

        corr_img = cross_image(current_frame, last_frame)
        cx, cy = np.unravel_index(np.argmax(corr_img), corr_img.shape)

        frame_count += 1
        if not frame_count % 10:
            fps = "{:.2f}".format(10 / (time.time() - last_time))
            last_time = time.time()

        info = [
                ("Shift", (sx - cx, sy - cy)),
                ("Point 1", (sx, sy)),
                ("Point 2", (cx, cy)),
                ("FPS", fps)
            ]

        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 255), 2)

        last_frame = current_frame

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            cv2.destroyAllWindows()
            break
        
