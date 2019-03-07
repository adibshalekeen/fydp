import argparse
import datetime
import time
import imutils
import cv2
from scipy.stats import norm
import numpy as np
from enum import Enum

class MotionDetectionParameter(Enum):
    fps = 0
    timeout = 1
    max_len = 2
    min_len = 3
    path = 4
    angle = 5
    path_encoding = 6

    def describe(self):
        return self.name, self.value
    
    def __str__(self):
        return '{0}'.format(self.name)

class MotionDetection:

    @staticmethod
    def remove_background(frame, subtractor):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fgmask = subtractor.apply(frame)
        return cv2.morphologyEx(fgmask, cv2.MORPH_ELLIPSE, kernel)

    @staticmethod
    def get_full_contours(current_frame, subtractor, downresScale):
        foreground = MotionDetection.remove_background(
            current_frame, subtractor)
        output = MotionDetection.channel_image(foreground, 0)

        contours = cv2.findContours(
            foreground.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[1]
        filtered_cntrs = []
        if len(contours) > 0:
            for i in range(0, len(contours)):
                if cv2.contourArea(contours[i]) > (20000 / (2 ** (downresScale + 2))):
                    filtered_cntrs.append(contours[i])
        x = 0
        y = 0
        height = foreground.shape[0]
        width = foreground.shape[1]
        if (len(filtered_cntrs) > 0):
            c = MotionDetection.centroid_from_contours(filtered_cntrs)
            x = c[0]/width
            y = c[1]/height

        # hull = cv2.convexHull(flat_list, False)
        # cv2.drawContours(output, filtered_cntrs, -1, (0, 255, 0), 1)
        # cv2.drawContours(output, hull, -1, (0, 255, 0), 1)
        cv2.drawContours(output, filtered_cntrs, -1, (0, 255, 0), 1)
        # cv2.drawContours(output, hull, -1, (0, 255, 0), 1)

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
        output[:, :, channel] = frame
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
    def add_frame_path_centroid(centroids, frame, color=(0, 255, 0)):
        height = frame.shape[0]
        width = frame.shape[1]
        if len(centroids[0][0]) < 1:
            return
        for i in range(1, len(centroids[0][0])):
            previous = (int(centroids[0][0][i - 1]*width),
                        int(centroids[0][1][i - 1]*height))
            current = (int(centroids[0][0][i]*width),
                       int(centroids[0][1][i]*height))
            cv2.line(frame, previous, current, color, int(np.ceil(height/150)))

    @staticmethod
    def process_image_contours(frame, subtractor, downresScale):
        frame_result, centroid = MotionDetection.get_full_contours(frame, subtractor, downresScale)
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
    def add_centroid(centroids, centroid, count, timeout):
        if centroid[0] != 0 and centroid[1] != 0:
            x = np.concatenate((centroids[0][0], np.array([centroid[0]])))
            y = np.concatenate((centroids[0][1], np.array([centroid[1]])))
            centroids = np.array([[x, y]])
            count = timeout
        else:
            count -= 1
        return count, centroids

    @staticmethod
    def test_path(centroids, count, timeout, max_len, min_len):
        point1 = None
        point2 = None
        if len(centroids) > max_len or count < 0:
            x = centroids[0][0]
            y = centroids[0][1]
            if len(x) > min_len:
                x_1 = x[0]
                x_2 = x[len(x) - 1]
                z = np.polyfit(x, y, 1)
                y_1 = z[0]*x_1 + z[1]
                y_2 = z[0]*x_2 + z[1]
                point1 = (x_1, y_1)
                point2 = (x_2, y_2)
            return timeout, np.array([[[], []]]), (point1, point2)
        return count, centroids, (point2, point1)

    @staticmethod
    def draw_fitted_path(frame, fitted_line, color=[0, 255, 0]):
        if fitted_line[0] is None or fitted_line[1] is None:
            return
        h = frame.shape[0]
        w = frame.shape[1]
        x_1 = int(fitted_line[0][0]*w)
        y_1 = int(fitted_line[0][1]*h)
        x_2 = int(fitted_line[1][0]*w)
        y_2 = int(fitted_line[1][1]*h)
        cv2.line(frame, (x_1, y_1), (x_2, y_2), color, int(np.ceil(h/150)))


    @staticmethod
    def get_fitted_path_stat(frame, fitted_line):
        h = frame.shape[0]
        w = frame.shape[1]
        x_1 = int(fitted_line[0][0]*w)
        y_1 = int(fitted_line[0][1]*h)
        x_2 = int(fitted_line[1][0]*w)
        y_2 = int(fitted_line[1][1]*h)
        vector = (x_2 - x_1, y_2 - y_1)
        angle = np.arctan2([vector[0]],[vector[1]])*(180/np.pi)
        encoding = MotionDetection.gesture(angle)
        print(fitted_line, vector, angle,encoding)
        return vector, angle, encoding

    @staticmethod
    def gesture(angle):
       abs_angle = np.abs(angle)
       encoding = 0
       for i in range(0,181,45):
           if abs_angle < i + 22.5:
               break
           encoding += 1
       if angle > 0:
           return 10 + encoding
       else:
           return 20 + encoding

    @staticmethod
    def showconfig(frame, selected_parameter, parameter_dict):
        font_size = frame.shape[0]/750
        items = list(parameter_dict.items())
        for i in range(0, len(items)):
            color = (0,0,255)
            if items[i][0] == selected_parameter:
                color = (0,255,0)
            cv2.putText(frame, str(items[i][0]) + ": " + str(items[i][1]),
                        (10, (i+1)*int(font_size*40)), cv2.FONT_HERSHEY_SIMPLEX, font_size, color, 1)
