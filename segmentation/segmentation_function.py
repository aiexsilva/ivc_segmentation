import numpy as np
import cv2

def open_camera():
    capture = cv2.VideoCapture(0)
    return capture

def segmentation(capture):
    ret, frame = capture.read()
    # making it so the camera is not mirrored
    frame = cv2.flip(frame, 1)

    if not ret:
        print("not able to grab frame")
        return exit(1)

    # makes it so the frame goes from rgb to hsv
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # lower threshold for green
    lower_green = np.array([35, 100, 50])
    # upper threshold for green
    upper_green = np.array([85, 255, 255])

    # this is for red, since red is in the beginning and end of the hsv color graph then u need 2 different ranges
    lower_red_1 = np.array([0, 150, 150])
    upper_red_1 = np.array([10, 255, 255])
    lower_red_2 = np.array([170, 150, 150])
    upper_red_2 = np.array([180, 255, 255])

    # mask the objects, shows in white our color and black the rest
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_red_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask_red_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

    # combine masks
    mask_red = mask_red_1 | mask_red_2

    # shows the actual color of the object instead of just white
    green_segmentation = cv2.bitwise_and(frame, frame, mask=mask_green)
    blue_segmentation = cv2.bitwise_and(frame, frame, mask=mask_red)

    # finds all the points that make up the contour of the "color block"
    # cv2.RETR_EXTERNAL only gets the external contour, the largest, ignoring any internal contours
    contours, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours2, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # show all windows in between the process
    cv2.imshow("green hsv", mask_green)
    cv2.imshow("red hsv", mask_red)
    cv2.imshow("green segmentation", green_segmentation)
    cv2.imshow("red segmentation", blue_segmentation)

    return frame, contours, contours2

def contours_main(frame, contours):
    largest_contour = max(contours, key=cv2.contourArea)
    # creates rectangle that bounds the largest contour found
    x, y, w, h = cv2.boundingRect(largest_contour)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # calculates center of that rectangle
    green_center = (x + w // 2, y + h // 2)

    return green_center

def contours2_main(frame, contours2):
    largest_contour_red = max(contours2, key=cv2.contourArea)
    a, b, c, d = cv2.boundingRect(largest_contour_red)
    cv2.rectangle(frame, (a, b), (a + c, b + d), (0, 0, 255), 2)

    red_center = (a + c // 2, b + d // 2)

    return red_center