from gestures import api
from gestures.image_processing import MotionDetection, MotionDetectionParameter
import cv2
import time
import numpy as np
import imutils
import requests
import multiprocessing

first = True
ip = "http://192.168.0.54:"
port = "2081/sendMeMessage"
url = ip + port
http_params = {'gesture': None}
    
camera_params = {
    "res":[640, 480],
    "fps":90
}

camera = api.Camera(5,
                    camera_params)

mdp = MotionDetectionParameter

persistent_args = {
    "bgSubtractor": cv2.createBackgroundSubtractorMOG2(history=1),
    "all_centroids": np.array([[[], []]]),
    "params": {MotionDetectionParameter.fps: 0,
               MotionDetectionParameter.timeout: 10,
               MotionDetectionParameter.max_len: 70,
               MotionDetectionParameter.min_len: 5,
               MotionDetectionParameter.path: (None, None),
               MotionDetectionParameter.angle: None,
               MotionDetectionParameter.path_encoding: None},
    "count": 10,
    "selected_param": MotionDetectionParameter.timeout
}

def show_camera_output(frame, **kwargs):
    object_centroid = kwargs["object_centroid"]
    all_centroids = kwargs["all_centroids"]
    fitted_line = kwargs["fitted_line"]
    selected_param = kwargs["selected_param"]
    params = kwargs["params"]

    frame = MotionDetection.add_frame_centroid(
        object_centroid, frame, (255, 255, 255))
    MotionDetection.add_frame_path_centroid(all_centroids, frame, (255, 255, 255))
    MotionDetection.draw_fitted_path(frame, fitted_line)
    MotionDetection.showconfig(frame, selected_param, params)

def update_func(new_vals, args):
    args["all_centroids"] = new_vals[0]
    args["count"] = new_vals[1]
    args["params"] = new_vals[2]
    args["selected_param"] = new_vals[3]

def processing_func(fulres, tasks, args):
    bgSubtractor = args["bgSubtractor"]
    all_centroids = args["all_centroids"]
    count = args["count"]
    params = args["params"]
    selected_param = args["selected_param"]

    downresScale = 2
    stime = time.time()
    frame = MotionDetection.downResImage(fulres, downresScale)

    foreground, object_centroid = MotionDetection.process_image_contours(
        frame, bgSubtractor, downresScale)

    count, all_centroids = MotionDetection.add_centroid(
        all_centroids, object_centroid, count, params[MotionDetectionParameter.timeout])

    count, all_centroids, fitted_line = MotionDetection.test_path(
        all_centroids,
        count, params[MotionDetectionParameter.timeout],
        params[MotionDetectionParameter.max_len],
        params[MotionDetectionParameter.min_len])

    if (fitted_line[0] is not None):
            params[MotionDetectionParameter.path], params[MotionDetectionParameter.angle], params[MotionDetectionParameter.path_encoding] = md.get_fitted_path_stat(fulres, fitted_line)
            gesture = MotionDetectionParameter.gesture_map[params[MotionDetectionParameter.path_encoding]]
            # try:
            #     requests.post(url=url, data=gesture + "|555")
            # except Exception:
            #     print("Victor done goofed")
            print(params)

    tasks.put(api.CameraWorkerTask(fulres,
                                   img_processor=show_camera_output,
                                   object_centroid=object_centroid,
                                   all_centroids=all_centroids,
                                   fitted_line=fitted_line,
                                   selected_param=selected_param,
                                   params=params))
    
    params[MotionDetectionParameter.fps] = int(1 / (time.time() - stime))
    print('FPS {:.1f}'.format(1 / (time.time() - stime)))
    return all_centroids, count, params, selected_param

camera.start_processing(processing_func, update_func, persistent_args)