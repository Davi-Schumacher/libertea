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

def detect_orientation(arrow_approximation: np.ndarray) -> str:
    """Checks the orientation of a pentagon approximation of an arrow

    Args:
        arrow_approximation (np.ndarray): A 5x2 numpy array giving the 5 x,y
        coordinate pairs of the pentagon used to approximate an arrow.

    Returns:
        str: "U" if up, "D" if down, "L" if left, "R" if right, else "X"
    """

    # Make sure a 5x2 numpy array was given
    assert isinstance(arrow_approximation, np.ndarray) and arrow_approximation.shape == (5, 2)
    
    # Calculate the medians and means of the x and y coordinates separately
    med_X, med_Y = np.median(arrow_approximation[:, 0]), np.median(arrow_approximation[:, 1])
    mean_X, mean_Y = np.mean(arrow_approximation[:, 0]), np.mean(arrow_approximation[:, 1])

    # Calculate the difference between mean and median for both x's and y's
    diff_X, diff_Y = mean_X - med_X, mean_Y - med_Y
    
    # A larger diff_X means the arrow is horizontal
    if np.abs(diff_X) > np.abs(diff_Y):
        
        # Mean to right of median indicates more point mass on right, arrow points left
        if diff_X > 0:
            return "L"
        # More point mass to the left, arrow points right
        else:
            return "R"
    
    # A larger diff_X means the arrow is horizontal
    else:

        # Same logic as above but think vertically
        if diff_Y > 0:
            return "U"
        else:
            return "D"

    # Give a bad return if something above didn't work
    return "X"


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

cv2.polylines(vis, hulls, 1, (0, 255, 0))

shape_detector = ShapeDetector()

mask = np.zeros((img.shape[0], img.shape[1], 1), dtype=np.uint8)

orientations, points = [], []
for contour in hulls:

    shape, peri, approx = shape_detector.detect(contour)
    
    if shape == "pentagon":
        
        if peri > 41 and peri < 44:

            reshaped = contour.reshape(contour.shape[0], contour.shape[2])
            mean_X, mean_Y = np.mean(reshaped[:, 0]), np.mean(reshaped[:, 1])
            
            # if mean_Y > 630 and mean_Y < 650 and mean_X > 750 and mean_X < 760:
            if mean_Y > 630 and mean_Y < 650:

                orientation = detect_orientation(approx.reshape(approx.shape[0], approx.shape[2]))
                orientations.append(orientation)
                points.append((int(mean_X), int(mean_Y)))
                cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1)


for o, p in zip(orientations, points):
    cv2.putText(vis, o, p, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

cv2.imshow("orientations", vis)
cv2.waitKey(0)

# #this is used to find only arrow regions, remaining are ignored
# masked = cv2.bitwise_and(img, img, mask=mask)

# blurred = cv2.GaussianBlur(masked, (5, 5), 0)

# edges = cv2.Canny(blurred, 100, 200)

