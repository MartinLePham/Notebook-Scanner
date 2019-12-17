# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to the input image")
ap.add_argument("-w", "--ppm", type=float, required=True,
                help="pixel per metric input)")
args = vars(ap.parse_args())
print(args)

# load the image, convert it to grayscale, and blur it slightly
image = cv2.imread(args["image"])

# convert it to grayscale and blur it slightly
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (7, 7), 0)

RS = cv2.resize(gray, (1600, 800))
cv2.imshow('gray', RS)

# perform edge detection, then perform a dilation + erosion to
# close gaps in between object edges
edged = cv2.Canny(gray, 50, 100)

# RS = cv2.resize(edged, (1600, 800))
# cv2.imshow('Canny', RS)

edged = cv2.dilate(edged, None, iterations=1) #14
edged = cv2.erode(edged, None, iterations=1) #11

RS = cv2.resize(edged, (1600, 800))
cv2.imshow('edged', RS)

# find contours in the edge map
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

# sort the contours from left-to-right
(cnts, _) = contours.sort_contours(cnts)

# initialize 'pixels per metric' calibration
pixelsPerMetric = float(args["ppm"]) #26.7826

# Hold corner coordinates
corners = []

# loop over the contours individually
for c in cnts:
    # if the contour is not sufficiently large, ignore it
    # if cv2.contourArea(c) > 16:
    #     continue
    # print(cv2.contourArea(c))
    # elif cv2.contourArea(c) > 2000:
    # 	continue

    # compute the rotated bounding box of the contour
    orig = image.copy()
    box = cv2.minAreaRect(c)
    box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
    box = np.array(box, dtype="int")

    # order the points in the contour such that they appear
    # in top-left, top-right, bottom-right, and bottom-left
    # order, then draw the outline of the rotated bounding
    # box
    box = perspective.order_points(box)
    corners.append(list(box[2]))
    corners.append(list(box[3]))

# bezel measurements
bezel_side = dist.euclidean(corners[0], corners[4])
bezel_top = dist.euclidean(corners[1], corners[5])
# ---- pixelspermetric calibration ----
bezel_side = float(bezel_side)/pixelsPerMetric
bezel_top = float(bezel_top)/pixelsPerMetric

# draw distances
for (x,y) in corners:
    cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

cv2.line(orig, (corners[0][0], corners[0][1]), (corners[4][0], corners[4][1]), (255, 0, 255), 2)
cv2.line(orig, (corners[1][0], corners[1][1]), (corners[5][0], corners[5][1]), (255, 0, 255), 2)


# show the output image
RS = cv2.resize(orig, (800, 800))
RS = cv2.rotate(RS, cv2.ROTATE_90_CLOCKWISE)

cv2.putText(RS, "{:.1f}mm".format(bezel_side),
	(400, 790), cv2.FONT_HERSHEY_SIMPLEX,
	0.65, (255, 255, 255), 2)
cv2.putText(RS, "{:.1f}mm".format(bezel_top),
	(10, 400), cv2.FONT_HERSHEY_SIMPLEX,
	0.65, (255, 255, 255), 2)

cv2.imshow("Image", RS)
cv2.waitKey(0)


