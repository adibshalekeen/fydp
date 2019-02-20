from picamera import PiCamera, PiCameraCircularIO
import time
import threading
import cv2
import numpy as np

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
        self._thread = None
        # camera module needs some time twarm up after init
        time.sleep(2)

    def take_picture(self):
        if self._camera is not None:
            frame = np.empty((self._true_resolution[0] * self._true_resolution[1] * 3,), dtype=np.uint8)
            self._camera.capture(frame, 'bgr')
            # open cv represents frames as row major so we need to flip the resolutions
            return frame.reshape((self._true_resolution[1], self._true_resolution[0], 3))[:self._resolution[1], :self._resolution[0], :]
