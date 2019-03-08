from picamera.array import PiRGBArray
from picamera import PiCamera, PiCameraCircularIO
import time
import threading
import io
import cv2
import numpy as np
from gestures import image_processing

class Camera:
    def __init__(self,
                 exposure_time, 
                 camera_params,
                 frame_callback,
                 outdir='captures',
                 pic_out_dir='img',
                 vid_out_dir='vid'):
        self._exposure_time = exposure_time
        self._resolution = camera_params["res"]
        self._framecallback = frame_callback
        x_remainder = self._resolution[0] % 16
        y_remainder = self._resolution[1] % 16
        self._true_resolution = [self._resolution[0] + x_remainder, self._resolution[1] + y_remainder]
        print(self._true_resolution)
        self._framerate = camera_params["fps"]
        self._camera = PiCamera(resolution=self._resolution, framerate=self._framerate)
        self._pic_out_dir = './' + outdir + '/' + pic_out_dir
        self._rawCapture = PiRGBArray(self._camera, size=(self._true_resolution[0], self._true_resolution[1]))
        # camera module needs some time twarm up after init
        time.sleep(2)

    def take_picture(self):
        if self._camera is not None:
            frame = np.zeros((self._true_resolution[0] * self._true_resolution[1] * 3,), dtype=np.uint8)
            self._camera.capture(frame, 'bgr', use_video_port=True)
            # open cv represents frames as row major so we need to flip the resolutions
            return frame.reshape((self._true_resolution[1], self._true_resolution[0], 3))[:self._resolution[1], :self._resolution[0], :]

    def start_processing(self, func, delta=False):
        mdp = image_processing.MotionDetectionParameter
        params = {
            mdp.fps: 0,
            mdp.timeout: 10,
            mdp.max_len: 70,
            mdp.min_len: 5,
            mdp.path: (None, None),
            mdp.angle: None,
            mdp.path_encoding: None
        }
        selected_param = mdp.timeout
        bgSubtractor = cv2.createBackgroundSubtractorMOG2(history=1)
        all_centroids = np.array([[[], []]])
        count = 10

        if delta:
            prev_frame = None
        for frame in self._camera.capture_continuous(self._rawCapture, format="bgr", use_video_port=True):
            image = frame.array
            if delta and prev_frame is None:
                prev_frame = image
                self._rawCapture.truncate(0)
                continue
            if delta:
                all_centroids, count, params, selected_param = func(image, bgSubtractor, all_centroids, count, params, selected_param)
                prev_frame = image
            else:
                func(image)
            self._rawCapture.truncate(0)