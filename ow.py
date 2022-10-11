# ow.py
# pmoe7
# Importing all modules
import cv2
import numpy as np
from math import pow, sqrt
from multiprocessing import Process, Queue
import mss
import mss.tools
from win32 import win32api
import pyautogui
import win32con
import time

# def union(a,b):
#     x = min(a[0], b[0])
#     y = min(a[1], b[1])
#     w = max(a[0]+a[2], b[0]+b[2]) - x
#     h = max(a[1]+a[3], b[1]+b[3]) - y
#     return (x, y, w, h)

# Calls the Windows API to simulate mouse movement events that are sent to OW
def mouse_move(x, y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)


# Determines if the Caps Lock key is pressed in or not
def is_activated():
    return win32api.GetAsyncKeyState(0x01) != 0


def locate_target(target):
    # compute the center of the contour
    moment = cv2.moments(target)
    if moment["m00"] == 0:
        return

    cx = int(moment["m10"] / moment["m00"])
    cy = int(moment["m01"] / moment["m00"])

    mid = SQUARE_SIZE / 2
    x = -(mid - cx) + 15 if cx < mid else cx - mid - 5
    y = -(mid - cy) + 15 if cy < mid else cy - mid - 10

    target_size = cv2.contourArea(target)
    distance = sqrt(pow(x, 2) + pow(y, 2))

    # There's definitely some sweet spot to be found here
    # for the sensitivity in regards to the target's size
    # and distance
    slope = ((1.0 / 4.0) - 1) / (MAX_TARGET_DISTANCE / target_size)
    multiplier = ((MAX_TARGET_DISTANCE - distance) / target_size) * slope + 1

    if is_activated():
        mouse_move(int(x * multiplier), int(y * multiplier))


# Specifying upper and lower ranges of color to detect in hsv formats
#lower = np.array([15, 150, 20])
#upper = np.array([300, 255, 255]) # (These ranges will detect Yellow)

# (H/2, (S/100) * 255, (V/100) * 255) 

lower = (150, 100, 100)    # HSV VALUES
upper = (155, 255, 255)

# green
#lower= np.array([50, 80, 80])   
#upper= np.array([100, 255, 255])

SQUARE_SIZE = 256
MAX_TARGET_DISTANCE = sqrt(2 * pow(SQUARE_SIZE, 2))


with mss.mss() as sct:
    # Part of the screen to capture
    monitor = {"top": 40, "left": 0, "width": SQUARE_SIZE, "height": SQUARE_SIZE}
    print("Aim 2.0 Running...")
    while True:
        last_time = time.time()
        x, y = pyautogui.position()
        monitor['left'] = int(x - SQUARE_SIZE/2)
        monitor['top'] =  int(y - SQUARE_SIZE/2)
        # Get raw pixels from the screen, save it to a Numpy array
        frame = np.array(sct.grab(monitor))
        hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mask = cv2.inRange(hsvFrame, lower, upper) # Masking the image to find our color
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Finding contours in mask image'

        #Finding position of all contours
        if len(contours) != 0:
            list_of_pts = [] 
            for ctr in contours:
                list_of_pts += [pt[0] for pt in ctr]

            ctr = np.array(list_of_pts).reshape((-1,1,2)).astype(np.int32)
            ctr = cv2.convexHull(ctr) # done.
            #print(len(ctr))
            #cv2.drawContours(frame, ctr, -1, (0,0,0), 3)
            locate_target(ctr)

        cv2.imshow("OW AimAssist 1.0", mask) # Displaying mask image
        #cv2.imshow("window", frame) # Displaying webcam image

        #print("fps: {}".format(1 / (time.time() - last_time)))

        # Press "q" to quit
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break

