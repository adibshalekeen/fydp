from picamera.array import PiRGBArray
from picamera import PiCamera, PiCameraCircularIO
import time
import multiprocessing
import io
import cv2
import numpy as np

class CameraWorkerProcess(multiprocessing.Process):
    def __init__(self, task_queue):
        multiprocessing.Process.__init__(self)
        self._task_queue = task_queue
    
    def run(self):
        proc_name = self.name
        while True:
            next_task = self._task_queue.get()
            if next_task is None:
                print("Goodbye Cruel World " + str(proc_name))
                self._task_queue.task_done()
                break
            next_task()
            self._task_queue.task_done()
        return

class CameraWorkerTask(object):
    def __init__(self, frame, img_processor=None, **kwargs):
        self._frame = frame
        self._img_processor = img_processor
        self._args = kwargs

    def __call__(self):
        if self._img_processor is not None:
            self._img_processor(self._frame, **self._args)
        cv2.namedWindow("Cam",cv2.WND_PROP_FULLSCREEN)
        cv2.imshow("Cam", self._frame)
        cv2.waitKey(1)

class Camera:
    def __init__(self,
                 exposure_time, 
                 camera_params,
                 outdir='captures',
                 pic_out_dir='img',
                 vid_out_dir='vid'):
        self._exposure_time = exposure_time
        self._resolution = camera_params["res"]
        x_remainder = self._resolution[0] % 16
        y_remainder = self._resolution[1] % 16
        self._true_resolution = [self._resolution[0] + x_remainder, self._resolution[1] + y_remainder]
        print(self._true_resolution)
        self._framerate = camera_params["fps"]
        self._camera = PiCamera(resolution=self._resolution, framerate=self._framerate)
        self._pic_out_dir = './' + outdir + '/' + pic_out_dir
        self._rawCapture = PiRGBArray(self._camera, size=(self._resolution[0], self._resolution[1]))
        # camera module needs some time twarm up after init
        time.sleep(2)

    def take_picture(self):
        if self._camera is not None:
            frame = np.zeros((self._true_resolution[0] * self._true_resolution[1] * 3,), dtype=np.uint8)
            self._camera.capture(frame, 'bgr', use_video_port=True)
            # open cv represents frames as row major so we need to flip the resolutions
            return frame.reshape((self._true_resolution[1], self._true_resolution[0], 3))[:self._resolution[1], :self._resolution[0], :]

    def start_processing(self, process_func, update_func, persistent_args):
        worker_task_queue = multiprocessing.JoinableQueue()
        camera_worker = CameraWorkerProcess(worker_task_queue)
        camera_worker.start()
        
        for frame in self._camera.capture_continuous(self._rawCapture, format="bgr", use_video_port=True):
            image = frame.array
            ret_val = process_func(image, worker_task_queue, persistent_args)
            if ret_val is not None:
                update_func(ret_val, persistent_args)
            self._rawCapture.truncate(0)