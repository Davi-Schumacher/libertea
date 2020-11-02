# Import packages
import argparse
import cv2
import imutils
import numpy as np
import sys

class ShapeDetector:

    def detect(self, contour):
        shape = "unidentified"
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)

        if len(approx) == 3:
            shape = "triangle"

        elif len(approx) == 4:
            (x, y, w, h) = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)

            shape = "square" if aspect_ratio >= 0.95 and aspect_ratio <= 1.05 else "rectangle"

        elif len(approx) == 5:
            shape = "pentagon"

        else:
            shape = "circle"

        return shape, peri, approx


ratio = 1.0

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--image", required=True, help="path to input image")
args = vars(parser.parse_args())

#Create MSER object
mser = cv2.MSER_create()

img = cv2.imread(args["image"])

#Convert to gray scale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
thresh = cv2.threshold(gray, 145, 150, cv2.THRESH_BINARY)[1]

vis = img.copy()

#detect regions in gray scale image
# regions, _ = mser.detectRegions(blurred)
regions, _ = mser.detectRegions(thresh)


hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]

# print(hulls[0])
# sys.exit(0)

cv2.polylines(vis, hulls, 1, (0, 255, 0))

# cv2.imshow('img', vis)

# cv2.waitKey(0)
# sys.exit(0)

shape_detector = ShapeDetector()

mask = np.zeros((img.shape[0], img.shape[1], 1), dtype=np.uint8)

orientations, points = [], []
for contour in hulls:

    shape, peri, approx = shape_detector.detect(contour)

    if shape == "pentagon":
        # peri = cv2.arcLength(contour, True)
        
        if peri > 41 and peri < 44:
            # print(peri)
            reshaped = contour.reshape(contour.shape[0], contour.shape[2])
            mean_X, mean_Y = np.mean(reshaped[:, 0]), np.mean(reshaped[:, 1])
            
            # if mean_Y > 630 and mean_Y < 650 and mean_X > 750 and mean_X < 760:
            if mean_Y > 630 and mean_Y < 650:

                # print(approx)
                h, w = np.max(reshaped[:, 1]) - np.min(reshaped[:, 1]), np.max(reshaped[:, 0]) - np.min(reshaped[:, 0])
                if h > w:
                    orientations.append("V")
                else:
                    orientations.append("H")
                points.append((int(mean_X), int(mean_Y)))
                cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1)

# print(means)
# sys.exit(0)

#this is used to find only text regions, remaining are ignored
masked = cv2.bitwise_and(img, img, mask=mask)

blurred = cv2.GaussianBlur(masked, (5, 5), 0)

edges = cv2.Canny(blurred, 100, 200)
for o, p in zip(orientations, points):
    cv2.putText(vis, o, p, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

cv2.imshow("orientations", vis)
cv2.waitKey(0)

# contours = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# contours = imutils.grab_contours(contours)

# mask = np.zeros((img.shape[0], img.shape[1], 1), dtype=np.uint8)
# for contour in contours:
#     moments = cv2.moments(contour)

#     if moments["m00"] == 0.0:
#         continue

#     contour_X = int((moments["m10"] / moments["m00"]) * ratio)
#     contour_Y = int((moments["m01"] / moments["m00"]) * ratio)
#     shape = shape_detector.detect(contour)

#     if shape == "pentagon":
#         cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1)

# masked = cv2.bitwise_and(img, img, mask=mask)

# cv2.imshow("masked", masked)
# cv2.waitKey(0)
