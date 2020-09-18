
import time

import cv2
import mss
import numpy

with mss.mss() as sct:
    # Part of the screen to capture
    monitor = {"top": 0, "left": 0, "width": 800, "height": 600}

    # Which tracker to use
    tracker, tracker_name = cv2.TrackerCSRT_create(), "CSRT"

    # Bounding box variable
    initBB = None
    
    frame_count = 0
    fps = 0.0
    last_time = time.time()

    while "Screen capturing":
        # Get raw pixels from the screen, save it to a Numpy array
        frame = numpy.array(sct.grab(monitor))[:, :, :3]
        (H, W) = frame.shape[:2]
        frame = cv2.UMat(frame)

        if initBB is not None:
            (success, box) = tracker.update(frame)

            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y-75), (x + w, y + h), (0, 255, 0), 2)

            frame_count += 1
            if not frame_count % 10:
                fps = "{:.2f}".format(10 / (time.time() - last_time))
                last_time = time.time()

            info = [
                ("Tracker", tracker_name),
                ("Success", "Yes" if success else "No"),
                ("FPS", fps),
            ]

            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 255), 2)


        # Display the picture
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            initBB = cv2.selectROI("Frame", frame, fromCenter=False, 
                                   showCrosshair=True)

            tracker.init(frame, initBB)

        # Display the picture in grayscale
        # cv2.imshow('OpenCV/Numpy grayscale',
        #            cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY))

        # Press "q" to quit
        if key == ord("q"):
            cv2.destroyAllWindows()
            break
