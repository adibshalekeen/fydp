from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
from scipy.stats import norm
import numpy as np

downresScale = 3

width = 281
height = 500

class MotionDetector:

    @staticmethod
    def threshold_frame(current, previous, threshold_value = 50):
        # ksize = 3
        # currentBlurred = cv2.GaussianBlur(current, (ksize, ksize), 0)
        # previousBlurred = cv2.GaussianBlur(previous, (ksize, ksize), 0)
        # delta = cv2.absdiff(previousBlurred, currentBlurred)
        delta = cv2.absdiff(current, previous)
        image_thresh = cv2.threshold(delta, threshold_value, 255, cv2.THRESH_BINARY)[1]
        # thresh = cv2.dilate(thresh, None, iterations=1)
        # thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        return image_thresh

    @staticmethod
    def get_full_contours(current, previous, channel):
        thresh = self.threshold_frame(current, previous, 75)
        output = self.channel_image(thresh, channel)

        im2, contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        new_contours = []
        if len(contours) > 0:
            for i in range(0, len(contours)):
                area = cv2.contourArea(contours[i])
                if cv2.contourArea(contours[i]) > (750 / (2 ** (downresScale + 2))):
                    new_contours.append(contours[i])
        x = 0
        y = 0
        if (len(new_contours) > 0):
            x, y = centroid_from_contours(new_contours)

        cv2.drawContours(output, new_contours, -1, (0,255,0), 1)
        return output, (x, y)

    @staticmethod
    def get_approx_contours(current, previous, channel):
        thresh = self.threshold_frame(current, previous)
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        output = self.channel_image(thresh, channel)

        filteredContours = []

        for c in contours:
            # if the contour is too small, ignore
            if cv2.contourArea(c) < 1000 / (2 ** (downresScale + 2)):
                continue
            # compute the bounding box for the contour, draw it on the frame
            (x, y, w, h) = cv2.boundingRect(c)
            filteredContours.append(cv2.boundingRect(c))
            # cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return output, filteredContours

    @staticmethod
    def relative_position(frameShape, contours):
        f_h = frameShape[0]
        f_w = frameShape[1]
        i = 0
        while i < len(contours): 
            # (x, y, w, h)
            c = contours[i]
            contours[i] = (c[0]/f_w, c[1]/f_h, c[2]/f_w, c[3]/f_h)
            i = i + 1
        return contours

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
    def process_approx_image_contours(frame, previousFrame):
        red,r_c = self.get_approx_contours(frame[:, :, 0], previousFrame[:, :, 0], 0)
        green,g_c = self.get_approx_contours(frame[:, :, 1], previousFrame[:, :, 1], 1)
        blue,b_c = self.get_approx_contours(frame[:, :, 2], previousFrame[:, :, 2], 2)
        r_c = self.relative_position(frame.shape, r_c)
        g_c = self.relative_position(frame.shape, g_c)
        b_c = self.relative_position(frame.shape, b_c)
        return red,r_c,green,g_c,blue,b_c

    @staticmethod
    def add_centroid(centroid, frame, color=(0,255,0)):
        x = int(centroid[0])
        y = int(centroid[1])
        if x > 0 and y > 0: 
            cv2.rectangle(frame, (x, y), (x + 10, y + 10), color, 1)
        return frame

    @staticmethod
    def process_image_contours(frame, previousFrame):
        red, r_c = self.get_full_contours(frame[:, :, 0], previousFrame[:, :, 0], 0)
        green, g_c = self.get_full_contours(frame[:, :, 1], previousFrame[:, :, 1], 1)
        blue, b_c = self.get_full_contours(frame[:, :, 2], previousFrame[:, :, 2], 2)

        red = self.add_centroid(r_c, red)
        green = self.add_centroid(g_c, green)
        blue = self.add_centroid(b_c, blue)
        return red, r_c, green, g_c, blue, b_c

    @staticmethod
    def centroid(thresh):
        moment = cv2.moments(thresh)
        if moment["m00"] > 0:
            cx = int(moment["m10"]/moment["m00"])
            cy = int(moment["m01"]/moment["m00"])
            return cx, cy
        return None

    @staticmethod
    def process_image_threshold(frame, previousFrame):
        red = threshold_frame(frame[:,:,0], previousFrame[:,:,0])
        green = threshold_frame(frame[:,:,1],previousFrame[:,:,1])
        blue = threshold_frame(frame[:,:,2],previousFrame[:,:,2])

        r_c = centroid(red)
        g_c = centroid(green)
        b_c = centroid(blue)

        red = channel_image(red, 0)
        if r_c is not None:
            x = int(r_c[0])
            y = int(r_c[1])
            cv2.rectangle(red, (x, y), (x + 5, y + 5), (0, 255, 0), 1)
        green = channel_image(green, 1)
        blue = channel_image(blue, 2)
        return red, green, blue

    @staticmethod
    def downResImage(frame, i): 
        if i == 0:
            return frame
        else:
            return cv2.pyrDown(downResImage(frame, i-1))

    @staticmethod
    def make_visual_output(frame, red, green, blue):
        frame = imutils.resize(frame, width=500)
        red = imutils.resize(red, width=500)
        green = imutils.resize(green, width=500)
        blue = imutils.resize(blue, width=500)
        out_h = red.shape[1]
        out_w = red.shape[0]
        out = np.zeros((out_w * 2, out_h * 2, 3))
        out[0:out_w, 0:out_h] = frame
        out[0:out_w, out_h:2*out_h, :] = red
        out[out_w:2*out_w, 0:out_h, :] = green
        out[out_w:2*out_w, out_h:2*out_h, :] = blue
        return out

    @staticmethod
    def average_centroid(*args):
        if len(args) == 0:
            return 0, 0
        sum_x = 0
        sum_y = 0
        count = 0
        for c in args:
            if c[0] == 0 and c[1] == 0:
                continue
            sum_x += c[0]
            sum_y += c[1]
            count += 1
        if count == 0: 
            return 0, 0
        return int(sum_x / count), int(sum_y / count)