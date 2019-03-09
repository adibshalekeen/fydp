from gestures import api
from gestures import image_processing
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

mdp = image_processing.MotionDetectionParameter

persistent_args = {
    "bgSubtractor": cv2.createBackgroundSubtractorMOG2(history=1),
    "all_centroids": np.array([[[], []]]),
    "params": {mdp.fps: 0, mdp.timeout: 10, mdp.max_len: 70, mdp.min_len: 5, mdp.path: (None, None), mdp.angle: None, mdp.path_encoding: None},
    "count": 10,
    "selected_param": image_processing.MotionDetectionParameter.timeout
}

def show_camera_output(frame, **kwargs):
    object_centroid = kwargs["object_centroid"]
    all_centroids = kwargs["all_centroids"]
    fitted_line = kwargs["fitted_line"]
    selected_param = kwargs["selected_param"]
    params = kwargs["params"]

    frame = image_processing.MotionDetection.add_frame_centroid(
        object_centroid, frame, (255, 255, 255))
    image_processing.MotionDetection.add_frame_path_centroid(all_centroids, frame, (255, 255, 255))
    image_processing.MotionDetection.draw_fitted_path(frame, fitted_line)
    image_processing.MotionDetection.showconfig(frame, selected_param, params)

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
    md = image_processing.MotionDetection
    mdp = image_processing.MotionDetectionParameter

    frame = md.downResImage(fulres, downresScale)

    foreground, object_centroid = md.process_image_contours(
        frame, bgSubtractor, downresScale)

    count, all_centroids = md.add_centroid(
        all_centroids, object_centroid, count, params[mdp.timeout])

    count, all_centroids, fitted_line = md.test_path(
        all_centroids,
        count, params[mdp.timeout],
        params[mdp.max_len],
        params[mdp.min_len])

    if (fitted_line[0] is not None):
            params[mdp.path], params[mdp.angle], params[mdp.path_encoding] = md.get_fitted_path_stat(fulres, fitted_line)
            gesture = mdp.gesture_map[params[mdp.path_encoding]]
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
    
    params[mdp.fps] = int(1 / (time.time() - stime))
    print('FPS {:.1f}'.format(1 / (time.time() - stime)))
    return all_centroids, count, params, selected_param

camera.start_processing(processing_func, update_func, persistent_args)