import argparse
import datetime
import time
import imutils
import cv2
from scipy.stats import norm
import numpy as np

downresScale = 2

GESTURE_TIMEOUT = 10
GESTURE_MAX_LENGTH = 70
GESTURE_MIN_LENGTH = 5

class MotionDetection:

    @staticmethod
    def remove_background(frame, subtractor):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        fgmask = subtractor.apply(frame)
        return cv2.morphologyEx(fgmask, cv2.MORPH_ELLIPSE, kernel)

    @staticmethod
    def get_full_contours(current_frame, subtractor):
	    foreground = MotionDetection.remove_background(current_frame, subtractor)
	    output = MotionDetection.channel_image(foreground, 0)

	    contours = cv2.findContours(foreground.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[1]
	    new_contours = []
	    if len(contours) > 0:
		    for i in range(0, len(contours)):
			    if cv2.contourArea(contours[i]) > (20000 / (2 ** (downresScale + 2))):
				    new_contours.append(contours[i])
	    x = 0
	    y = 0
	    height = foreground.shape[0]
	    width = foreground.shape[1]
	    if (len(new_contours) > 0):
		    c = MotionDetection.centroid_from_contours(new_contours)
		    x = c[0]/width
		    y = c[1]/height

	    cv2.drawContours(output, new_contours, -1, (0,255,0), 1)
	    return output, (x, y)

    @staticmethod
    def centroid_from_contours(contours):
	    x_sum = 0
	    y_sum = 0
	    count = 0
	    for c in contours:
		    count += c.shape[0]
		    sum = np.sum(c, axis=0)
		    x_sum += sum[0, 0]
		    y_sum += sum[0, 1]
	    return int(x_sum / count), int(y_sum / count)

    @staticmethod
    def channel_image(frame, channel):
        output = np.zeros((frame.shape[0], frame.shape[1], 3))
        output[:,:,channel] = frame
        return output

    @staticmethod
    def add_frame_centroid(centroid, frame, color=(0, 255, 0)):
        height = frame.shape[0]
        width = frame.shape[1]
        x = int(centroid[0]*width)
        y = int(centroid[1]*height)
        if x > 0 and y > 0:
            cv2.rectangle(frame, (x, y), (x + int(height/15), y +
                                          int(height/15)), color, int(height/150))
        return frame
            
    @staticmethod
    def add_frame_path_centroid(centroids, frame, color=(0,255,0)):
    	height = frame.shape[0]
    	width = frame.shape[1]
    	if len(centroids[0][0]) < 1:
    		return
    	for i in range(1, len(centroids[0][0])):
    		previous = (int(centroids[0][0][i - 1]*width), int(centroids[0][1][i - 1]*height))
    		current = (int(centroids[0][0][i]*width), int(centroids[0][1][i]*height))
    		cv2.line(frame, previous, current, color, int(np.ceil(height/150)))

    @staticmethod
    def process_image_contours(frame, subtractor):
	    frame_result, centroid = MotionDetection.get_full_contours(frame, subtractor)
	    return frame_result, centroid

    @staticmethod
    def centroid(thresh):
        moment = cv2.moments(thresh)
        if moment["m00"] > 0:
            cx = int(moment["m10"]/moment["m00"])
            cy = int(moment["m01"]/moment["m00"])
            return cx, cy
        return None

    @staticmethod
    def downResImage(frame, i): 
        if i == 0:
            return frame
        else:
            return cv2.pyrDown(MotionDetection.downResImage(frame, i-1))
    
    @staticmethod
    def make_visual_output(resizeFrame=True, *args):
	    h = None
	    w = None
	    if len(args) < 0:
		    return
	    dimension = int(np.ceil(len(args)**0.5))
	    out = np.array([])
	    for i in range(0, len(args)):
		    frame = None
		    if resizeFrame:
			    frame = imutils.resize(args[i], width=500)
		    else:
			    frame = args[i]
		    if h is None:
			    h = frame.shape[0]
			    w = frame.shape[1]
			    out = np.ones((h*dimension, w*dimension, 3)) * 255

		    row = int(np.floor(i / dimension))
		    column = i % dimension
		    out[row*h:(row+1)*h, column*w:(column+1)*w, :] = frame
	    return out

    @staticmethod
    def add_centroid(centroids, centroid, count):
	    if centroid[0] != 0 and centroid[1] != 0:
		    x = np.concatenate((centroids[0][0], np.array([centroid[0]])))
		    y = np.concatenate((centroids[0][1], np.array([centroid[1]])))
		    centroids = np.array([[x,y]])
		    count = GESTURE_TIMEOUT
	    else: 
		    count -= 1
	    return count, centroids

    @staticmethod
    def test_path(centroids, count):
    	point1 = None
    	point2 = None
    	if len(centroids) > GESTURE_MAX_LENGTH or count < 0:
    		x = centroids[0][0]
    		y = centroids[0][1]
    		if len(x) > GESTURE_MIN_LENGTH and len(y) > GESTURE_MIN_LENGTH:
    			x_1 = x[0]
    			x_2 = x[len(x) - 1]
    			z = np.polyfit(x,y,1)
    			y_1 = z[0]*x_1 + z[1]
    			y_2 = z[0]*x_2 + z[1]
    			point1 = (x_1, y_1)
    			point2 = (x_2, y_2)
    		return GESTURE_TIMEOUT, np.array([[[], []]]), (point1,point2)
    	return count, centroids, (point1, point2)

    @staticmethod
    def draw_fitted_path(frame, fitted_line, color=[0,255,0]):
    	if fitted_line[0] is None or fitted_line[1] is None:
    		return
    	h = frame.shape[0]
    	w = frame.shape[1]
    	x_1 = int(fitted_line[0][0]*w)
    	y_1 = int(fitted_line[0][1]*h)
    	x_2 = int(fitted_line[1][0]*w)
    	y_2 = int(fitted_line[1][1]*h)
    	cv2.line(frame, (x_1,y_1), (x_2, y_2), color, 2)

