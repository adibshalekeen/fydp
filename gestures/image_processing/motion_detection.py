import argparse
import datetime
import time
import imutils
import cv2
from scipy.spatial import distance
import numpy as np
from enum import Enum

class MotionDetectionParameter():
    fps = 0
    timeout = 1
    max_len = 2
    min_len = 3
    path = 4
    angle = 5
    path_encoding = 6
    gesture_cooldown = 10
    gesture_map = {12:"Up", 
                   11:"TopLeft",
                   10:"Left",
                   20:"Left",
                   21:"BottomLeft",
                   22:"Down",
                   13:"TopRight",
                   24:"Right",
                   14:"Right",
                   23:"BottomRight"}
    min_centroid_count = 11

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
        # kernel = np.ones((5,5),np.uint8)
        # foreground = cv2.erode(foreground,kernel,iterations=1)
        # foreground = cv2.dilate(foreground,kernel,iterations=2)

        output = MotionDetection.channel_image(foreground, 0)

        contours = cv2.findContours(foreground, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        filtered_cntrs = []
        if len(contours) > 0:
            for i in range(0, len(contours)):
                if cv2.contourArea(contours[i]) > (1000 / (2 ** (downresScale + 2))):
                    filtered_cntrs.append(contours[i])
        x = 0
        y = 0
        height = foreground.shape[0]
        width = foreground.shape[1]
        if (len(filtered_cntrs) > 0):
            c = MotionDetection.centroid_from_contours(filtered_cntrs)
            x = c[0]/width
            y = c[1]/height

        cv2.drawContours(output, filtered_cntrs, -1, (0, 255, 0), 1)
        return output, (x, y)

    @staticmethod
    def centroid_from_contours(contours):
        min_y = 1000
        x = 0
        for c in contours:
            min_ys = np.where(c[:,0,1] == np.min(c[:,0,1]))[0]
            min_index = min_ys[len(min_ys) - 1]
            y = c[min_index,0,1]
            if y < min_y:
                min_y = y
                x = c[min_index,0,0]
        return x, min_y

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
            current = (int(centroids[0][0][i]*width),
                       int(centroids[0][1][i]*height))
            cv2.circle(frame, current, 5, (0,255,0), thickness=5)

    @staticmethod
    def process_image_contours(frame, subtractor, downresScale):
        return MotionDetection.get_full_contours(frame, subtractor, downresScale)

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

    # @staticmethod
    # def is_centroid_valid_avg_distance(centroids, centroid, avg_centroid_distance):
    #     length = len(centroids[0][0])
    #     if length > 1:
    #         prv_x = centroids[0][0][length - 1]
    #         prv_y = centroids[0][1][length - 1]
    #         current_distance = distance.euclidean((prv_x, prv_y), centroid))
    #         if avg_centroid_distance is not None:
    #             avg_centroid_distance = current_distance
    #         else:
    #             avg_centroid_distance = (avg_centroid_distance * length +  / 
    #     return avg_centroid_distance

    @staticmethod
    def add_centroid(centroids, centroid, count, timeout, avg_centroid_distance):
        if centroid[0]!=0 and centroid[1]!=0:
            x = np.concatenate((centroids[0][0], np.array([centroid[0]])))
            y = np.concatenate((centroids[0][1], np.array([centroid[1]])))
            centroids = np.array([[x, y]])
            count = timeout
        else:
            count -= 1
        return count, centroids, avg_centroid_distance
    
    @staticmethod
    def filter_centroids(centroids, start_dropout, end_dropout):
        length = len(centroids[0][0])
        # backElementToRemove = int(np.floor(length * start_dropout))
        # frontElementToRemove = int(np.floor(length * end_dropout))
        # centroids[0,0,0:backElementToRemove + 1] = np.average(centroids[0][0])
        # centroids[0,0,length - frontElementToRemove : length] = np.average(centroids[0][0])
        # centroids[0,1,0:backElementToRemove+1] = np.average(centroids[0][1])
        # centroids[0,1,length - frontElementToRemove : length] = np.average(centroids[0][1])
        return centroids[0][0][1:length-2], centroids[0][1][1:length-2]

    @staticmethod
    def test_path(centroids, count, timeout, max_len, min_len, min_centroid_count, start_dropout, end_dropout, avg_centroid_distance):
        point1 = None
        point2 = None
        length = len(centroids[0][0])
        if length > max_len or count < 0:
            x = centroids[0][0]
            y = centroids[0][1]
            if length > min_centroid_count:
                # truncate before and after
                x, y = MotionDetection.filter_centroids(centroids, start_dropout, end_dropout)
            if length > 2:
                delta_x = np.max(x) - np.min(x)
                delta_y = np.max(y) - np.min(y)
                distance_travelled = np.sqrt(delta_x**2 + delta_y**2)
                if distance_travelled > min_len:
                    x_max = np.max(x)
                    x_min = np.min(x)
                    y_max = np.max(y)
                    y_min = np.min(y)

                    x_min_index = np.where(x==x_min)[0][0]
                    x_max_index = np.where(x==x_max)[0][0]
                    y_min_index = np.where(y==y_min)[0][0]
                    y_max_index = np.where(y==y_max)[0][0]
                    
                    x_range = x_max - x_min
                    y_range = y_max - y_min

                    if x_range >= y_range:
                        min_index = x_min_index
                        max_index = x_max_index
                    else:
                        min_index = y_min_index
                        max_index = y_max_index

                    x_1 = x[np.min((min_index, max_index))]
                    x_2 = x[np.max((min_index, max_index))]
                    z = np.polyfit(x,y,1)
                    y_1 = z[0]*x_1 + z[1]
                    y_2 = z[0]*x_2 + z[1]
                    point1 = (x_1, y_1)
                    point2 = (x_2, y_2)
            return timeout, np.array([[[], []]]), (point1, point2), None
        return count, centroids, (point2, point1), avg_centroid_distance

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
        vector = (x_2 - x_1, y_1 - y_2)
        angle = np.arctan2(vector[1],vector[0])*(180/np.pi)
        encoding = MotionDetection.gesture(angle)
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
