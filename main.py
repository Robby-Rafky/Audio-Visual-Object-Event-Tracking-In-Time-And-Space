import numpy as np
import cv2
import imutils
import math
import pyglet
import time

# import and preload audio to be manipulated
music = pyglet.resource.media("pentakill.mp3", streaming=False)
player = pyglet.media.Player()
player.queue(music)
# init the audio player
player.play()
player.pause()

# values for Perceived focal length
object_real_width = 5
perceived_focal_length = (36*100)/object_real_width

# colour bounds for tracking target (green ball)
colour_lower = (35, 10, 10)
colour_upper = (80, 255, 255)

# keeps track of the status of the last tracking frame
last_frame_tracked = False

# pull video feed from LAN camera
camera_feed = cv2.VideoCapture("http://192.168.0.12:8081/video")
# small pause to allow the video capture to init fully
time.sleep(2)

while True:
    # load up the next frame from the video feed
    check, current_frame = camera_feed.read()

    # when the video feed is down, it will exit
    if not check:
        break

    # smaller working frame to reduce workload
    current_frame = cv2.resize(current_frame, (800, 450))

    if last_frame_tracked:
        # define new boundaries based on previous tracking data, limit the values to remain within original frame
        start_x = np.clip((x - (radius * 3)), 0, 800)
        start_y = np.clip((y - (radius * 3)), 0, 450)
        end_x = np.clip((x + (radius * 3)), 0, 800)
        end_y = np.clip((y + (radius * 3)), 0, 450)
        # crop image to the immediate area surrounding the tracked object
        local_frame = current_frame[start_y:end_y, start_x:end_x]
        # define new frame of reference for future calculations
        x_offset = start_x
        y_offset = start_y
        # draw current tracking range
        cv2.rectangle(current_frame, (start_x, start_y), (end_x, end_y), (0, 0, 255), 5)
    else:
        # otherwise default to whole frame tracking
        x_offset = 0
        y_offset = 0
        local_frame = current_frame

    # apply a gaussian blur convolution to the current frame (smoothen image, reduce high freq noise)
    blurred_frame = cv2.GaussianBlur(local_frame, (15, 15), 0)
    # convert image to the HSV colour space
    shifted_colour_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
    # create a binary mask of the frame using the colour range
    binary_mask = cv2.inRange(shifted_colour_frame, colour_lower, colour_upper)

    # erosion to eliminate noise, dilation to reduce the effects of erosion on non-noise data
    binary_mask = cv2.erode(binary_mask, None, iterations=3)
    binary_mask = cv2.dilate(binary_mask, None, iterations=3)
    # find contours in the binary mask
    contours = cv2.findContours(binary_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    centre = None

    # when anything is tracked
    if len(contours) > 0:
        last_frame_tracked = True
        player.play()

        # find the largest contour (sorted by area), obtain its position and size data with the minimum radius that fits
        centroid = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(centroid)
        # calculate the centre of the chosen contour
        mat = cv2.moments(centroid)
        centre = (int(mat["m10"] / mat["m00"]) + x_offset, int(mat["m01"] / mat["m00"]) + y_offset)

        # update frame of reference
        x = x + x_offset
        y = y + y_offset

        # draw a circle enclosing the contour with a dot in the centre
        cv2.circle(current_frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
        cv2.circle(current_frame, centre, 5, (0, 0, 255), -1)

        # apply formula to calculate distance given the real world parameters of the tracked object
        distance = (object_real_width * perceived_focal_length) / (radius * 2)
        # frame centre to tracking centre line
        cv2.line(current_frame, (400, 225), (math.floor(x), math.floor(y)), (0, 0, 0), 4)

        # data conversion from pixels to cm
        pixel_ratio = 5.0 / (2.0 * radius)
        x_real = (x - 400.0) * pixel_ratio
        y_real = (225 - y) * pixel_ratio
        # data type conversion for next frame tracking location calculations
        x = int(x)
        y = int(y)
        radius = int(radius)
        # position the audio player in the space
        player.position = ((x_real/3), (y_real/3), (distance/3))

        # update active pyglet loops with external changes (the player class with the new player.position data)
        pyglet.clock.tick()
    else:
        # nothing found, stop the music
        last_frame_tracked = False
        player.pause()

    # show the window with the video feed
    cv2.imshow("Live Camera Feed", current_frame)
    cv2.imshow("Local Area", local_frame)
    # cv2.imshow("test", shifted_colour_frame)

    cv2.waitKey(1)

cv2.destroyAllWindows()
