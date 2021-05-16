# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
ap.add_argument("-w", "--width", type=float, required=True,
	help="width of the left-most object in the image (in inches)")
args = vars(ap.parse_args())
print(args)

# load the image, convert it to grayscale, and blur it slightly
image = cv2.imread(args["image"])
# convert it to grayscale and blur it slightly
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (7, 7), 0) # 1

RS = cv2.resize(gray, (1000, 500))
# cv2.imshow('gray', RS)

# perform edge detection, then perform a dilation + erosion to
# close gaps in between object edges
edged = cv2.Canny(gray, 50, 100) #50, 125
edged = cv2.dilate(edged, None, iterations=1) # 11
edged = cv2.erode(edged, None, iterations=1) # 14

# find contours in the edge map
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
# print(cnts)
conts = imutils.grab_contours(cnts)
# print(cnts)

RS = cv2.resize(edged, (800, 400))
cv2.imshow("Edged_g0", RS)
box_list = []
# sort the contours from left-to-right and initialize the
# 'pixels per metric' calibration variable
(cnts, _) = contours.sort_contours(conts)
pixelsPerMetric = None
centers = []
# loop over the contours individually
for c in cnts:
	# if the contour is not sufficiently large, ignore it
	# print('c = ' + str(c))
	# print('area of c =' + str(cv2.contourArea(c)))
	# print(cv2.contourArea(c))
	# if cv2.contourArea(c) > 100:
	# 	continue

	# compute the rotated bounding box of the contour
	orig = image.copy()
	box = cv2.minAreaRect(c)
	box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
	# print(box)
	box = np.array(box, dtype="int")
	# print(box)

	# order the points in the contour such that they appear
	# in top-left, top-right, bottom-right, and bottom-left
	# order, then draw the outline of the rotated bounding
	# box
	box = perspective.order_points(box)
	box_list.append(box)
	# print(box)
	# print('box = ' + str(box))
	cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

	RS = cv2.resize(orig, (1000, 500))
	cv2.imshow('cnts', RS)

	# loop over the original points and draw them
	for (x, y) in box:
		cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

	# unpack the ordered bounding box, then compute the midpoint
	# between the top-left and top-right coordinates, followed by
	# the midpoint between bottom-left and bottom-right coordinates
	(tl, tr, br, bl) = box
	(tltrX, tltrY) = midpoint(tl, tr)
	(blbrX, blbrY) = midpoint(bl, br)

	# compute the midpoint between the top-left and bottom-left points,
	# followed by the midpoint between the top-right and bottom-right
	(tlblX, tlblY) = midpoint(tl, bl)
	(trbrX, trbrY) = midpoint(tr, br)

	# draw the midpoints on the image
	cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
	cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
	cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
	cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

	# draw lines between the midpoints
	cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
		(255, 0, 255), 2)
	cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
		(255, 0, 255), 2)

	# compute the Euclidean distance between the midpoints
	dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
	dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

	# if the pixels per metric has not been initialized, then
	# compute it as the ratio of pixels to supplied metric
	# (in this case, inches)
	if pixelsPerMetric is None:
		pixelsPerMetric = dB / args["width"]

	# print(pixelsPerMetric)
	# compute the size of the object
	dimA = dA / pixelsPerMetric
	dimB = dB / pixelsPerMetric

	# draw the object sizes on the image
	cv2.putText(orig, "{:.1f}mm".format(dimA),
		(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (255, 255, 255), 2)
	cv2.putText(orig, "{:.1f}mm".format(dimB),
		(int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (255, 255, 255), 2)

	# show the output image
	RS = cv2.resize(orig, (1600, 800))
	# cv2.imshow("Image", RS)
	cv2.waitKey(0)

	# Find center point of contours:
	M = cv2.moments(c)
	cX = int(M['m10'] / M['m00'])
	cY = int(M['m01'] / M['m00'])
	centers.append([cX, cY])

# Find the distance D between the two contours:
if len(centers) >= 2:
	dx = centers[0][0] - centers[1][0]
	dy = centers[0][1] - centers[1][1]
	D = np.sqrt(dx * dx + dy * dy)
	D = D / pixelsPerMetric
	# print(D)
	# print(centers)

	# draw lines between the midpoints
	cv2.line(edged, (centers[0][0], centers[0][1]), (centers[1][0], centers[1][1]),
		(255, 0, 255), 2)
	cv2.putText(edged, "{:.1f}mm".format(D),
		(centers[0][0], centers[0][1]), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (255, 255, 255), 2)
	cv2.circle(edged, (centers[0][0], centers[0][1]), 5, (0, 180, 255), -1)
	cv2.circle(edged, (centers[1][0], centers[1][1]), 5, (0, 180, 255), -1)

	RS = cv2.resize(edged, (1600, 800))
	cv2.imshow("edged", RS)
	cv2.waitKey(0)