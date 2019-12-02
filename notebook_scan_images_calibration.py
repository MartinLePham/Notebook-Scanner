# USAGE
# python fps_demo.py
# python fps_demo.py --display 1

# import the necessary packages
# from __future__ import print_function
import imutils
from imutils.video import WebcamVideoStream
from imutils import contours
from imutils import perspective
from scipy.spatial import distance as dist
import numpy as np
import argparse
import cv2
import serial
import time
from pyspin import PySpin
from PIL import Image
import matplotlib.pyplot as plt
import os

arduinoData = serial.Serial('com7', 9600, timeout=1)
x_limit = None
edges_x = []
edges_y = []
edge = None
middle_screen = 0
StartY = None
StopY = None
Key = None
Motion = None
start_scan = None

def save_image(edged, image_number, scan_type):
    frame_filename = "Scan_%d_Frame_%d_at_time_%d.jpg" % (scan_type, image_number, time.process_time() - start_timer)
    loc_n_name = os.path.join(folder, frame_filename)
    image_transform = Image.fromarray(edged)
    image_transform.save(loc_n_name)
    print('Frame Number: %d taken at %d' % (image_number, time.process_time() - start_timer))
    image_number += 1

def edge_FOV(cnts, edged, edges_list):
    (cnts, _) = contours.sort_contours(cnts)
    for c in cnts:
        if cv2.contourArea(c) < 100:  # noise reduction (3500 - 4000)
            # cnts.remove(c)
    (h, w) = edged.shape
    color_mid = edged[int(h / 2), int(w / 2)]
    if color_mid == 255:  # color at mid of screen
        print("[INFO] Found Edge... Recording Data...")
        arduinoData.write(b'F')  # ---- TELL ARDUINO WE FOUND EDGE AT PIXEL ----
        time.sleep(1)  # Wait for arduino to record distance data
        edge = arduinoData.readline().decode("ASCII").strip("\n").strip("\r")  # ---- RETRIEVE EDGE POSITION FROM ARDUINO ----
        edges_list.append(edge)  # dependent on x or y
    else:
        arduinoData.write(b'S')  # ---- TELL ARDUINO VIDEO DETECTED EDGE (SLOW DOWN)
        print("[INFO] Camera slowing...")
        # -------- PID Controller ---------

def edge_scan_x(edged):
    print("[INFO] X Scan in progress...")
    save_image(edged, image_number, scan_type="x")
    # find contours in the edges map
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    if len(cnts) > 0:
        edged_FOV(cnts, edged, edges_x)
        # plot images from scans
        plt.imshow(edged, cmap='gray')
        plt.pause(0.001)
        plt.clf()
    else:
        x_limit = arduinoData.readline().decode("ASCII").strip("\n").strip("\r")  # stop x scan (should keep reading 'found' or 'fast')
        arduinoData.write(b'fast')

def edge_scan_y(edged):
    print("[INFO] Y Scan in progress...")
    save_image(edged, image_number, scan_type="y")
    # find contours in the edges map
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    if len(cnts) > 0:
        edge_FOV(cnts, edged, edges_y)
        # plot images from scans
        plt.imshow(edged, cmap='gray')
        plt.pause(0.001)
        plt.clf()
    else:
        arduinoData.write(b'fast')



# ------- MAIN CODE -------
# set image save location
folder = "C:\\Users\\marti\\MyScripts\\Imaging\\size-of-objects\\Laptop Frames"
# clear folder
for file in os.listdir(folder):
    file_path = os.path.join(folder, file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

# find Camera from System
system = PySpin.System.GetInstance()
cam_list = system.GetCameras()
cam = cam_list[0]

# initialize camera
nodemap_tldevice = cam.GetTLDeviceNodeMap()
cam.Init()
nodemap = cam.GetNodeMap()
# camera framerate
node_acquisition_framerate = PySpin.CFloatPtr(nodemap.GetNode('AcquisitionFrameRate'))
framerate_to_set = node_acquisition_framerate.GetValue()
print('[INFO] Frame rate to be set to %d...' % framerate_to_set)

cam.BeginAcquisition()

# start arduino motion
print("[INFO] Initializing Motion...")
time.sleep(5)  # allow arduino to warm-up
arduinoData.write(b'G')

# file name descriptions
image_number = 1
start_timer = time.process_time()

# continuously take images
while 1:
    # image capture
    image_result = cam.GetNextImage()
    width = image_result.GetWidth()
    height = image_result.GetHeight()

    # ------- Canny edge detection ---------
    # image data conversion
    rawFrame = np.array(image_result.GetData(), dtype="uint8").reshape((height, width))
    frame = cv2.cvtColor(rawFrame, cv2.COLOR_BAYER_RG2GRAY)

    # grayscale image
    gray = cv2.GaussianBlur(frame, (7, 7), 0)

    # perform edge detection, then perform a dilation + erosion to
    # close gaps in between object edges
    edged = cv2.Canny(gray, 50, 100)
    edged = cv2.dilate(edged, None, iterations=4)
    edged = cv2.erode(edged, None, iterations=1)
    # cv2.imshow('edged', edged)
    # cv2.waitKey(1000)

    # plt.imshow(edged, cmap='gray')
    # plt.pause(0.001)
    # plt.clf()
    # print('Frame Number: %d; Width: %d; Height: %d' % (number, width, height))
    # number += 1

    # scanning dependencies
    if start_scan != "Scan":  # wait to start scanning
        start_scan = arduinoData.readline().decode("ASCII").strip("\n").strip("\r")
        # for element in start_scan:
        #     print("%d %d", (image_number, element))
        #     image_number += 1
        # print(start_scan)
    elif start_scan == "Scan":
        print("START_SCAN = START_SCAN")
        if x_limit != "x_limit":
            edge_scan_x(edged)
        elif middle_screen == 0:
            print("[INFO] X Limit reached... Positioning for Y Scan...")
            middle_screen = (edges_x[-1] - edges_x[0]) / 2
            arduinoData.write(middle_screen.encode())
        # python in limbo... awaiting arduino scan command
        if StartY != "StartY":
            StartY = arduinoData.readline().decode("ASCII").strip("\n").strip("\r")  # should read "middle_screen' until arduino says "StartY"
        elif StartY == "StartY":
            StopY = arduinoData.readline().decode("ASCII").strip("\n").strip("\r")
            if StopY == "StopY":  # after hitting precision switch
                print("[INFO] Bottomed Out...")
                break  # end video
            else:
                edge_scan_y(edged)

    image_result.Release()
# key = cv2.waitKey(1) & 0xFF
# if key == ord("q"):
# 	break
time.sleep(1)

# ---- CALCULATIONS ----
system_x = edges_x[-1] - edges_x[0]
system_y = edges_y[-1] - edges_y[0] + 10  # MOUNT CALIBRATION REQUIRED
length_edges_x = len(edges_x)
length_edges_y = len(edges_y)
# AA_x =
# AA_y =

# ---- WAIT FOR ARDUINO SIGNAL TO TAKE PIC -----
num_pic = 2
while 1:
    take_pic = arduinoData.readline().decode("ASCII").strip("\n").strip("\r")
    if num_pic == 2:
        if take_pic == 'pic':
            print('[INFO] Taking Top-Left Picture...')
            # ---- save pic ----
            # ---- contour_distance.py ----
            time.sleep(5)
            arduinoData.write('more'.encode())
            num_pic -= 1
    elif num_pic == 1:
        if take_pic == 'pic':
            print('[INFO] Taking Top-Right Picture...')
            # ---- save pic ----
            # ---- contour_distance.py ----
            time.sleep(5)
            # arduinoData.write('more'.encode())
            num_pic -= 1
    else:
        break

# ---- OUTPUT DIMENSIONS ----

# do a bit of cleanup
cam.EndAcquisition()
cam.DeInit()
del cam
cam_list.Clear()
system.ReleaseInstance()
cv2.destroyAllWindows()
close('all')
