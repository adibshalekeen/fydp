from gestures import api
from gestures.image_processing import MotionDetection, MotionDetectionParameter
from audio_processing import HotWordDetection
import cv2
import time
import numpy as np
import imutils
import requests
import multiprocessing

ip = "http://localhost:"
port = "2080/sendMessage"
url = ip + port
http_params = {'gesture': None}

LIBRARY_PATH =  './audio_processing/libpv_porcupine.so'
MODEL_FILE_PATH = './audio_processing/porcupine_params.pv'
#KEYWORD_FILE_PATHS = ['./audio_processing/keyword_files/bumblebee_raspberrypi.ppn', './audio_processing/keyword_files/grapefruit_raspberrypi.ppn']

KEYWORD_FILE_PATHS = ['./audio_processing/keyword_files/kitchen_linux.ppn', './audio_processing/keyword_files/bedroom_linux.ppn']^M

camera_params = {
    "res":[640, 480],
    "fps":90
}

camera = api.Camera(5, camera_params)

wordDetector = HotWordDetection(
    library_path=LIBRARY_PATH,
    model_file_path=MODEL_FILE_PATH,
    keyword_file_paths=KEYWORD_FILE_PATHS
)

persistent_args = {
    "bgSubtractor": cv2.createBackgroundSubtractorMOG2(history=4),
    "all_centroids": np.array([[[], []]]),
    "active": None,
    "params": {MotionDetectionParameter.fps: 0,
               MotionDetectionParameter.timeout: 5,
               MotionDetectionParameter.gesture_cooldown: 20,
               MotionDetectionParameter.max_len: 8,
               MotionDetectionParameter.min_len: 0.15,
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
    encoding = params[MotionDetectionParameter.path_encoding]
    if encoding is not None:
        gesture = MotionDetectionParameter.gesture_map[encoding]
        font_size = frame.shape[0]/750
        cv2.putText(frame, "Gesture" + ": " + gesture,
                            (10, (len(params)+1)*int(font_size*40)), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0,0,255), 1)

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

    if args["active"] is None:

        encoding = params[MotionDetectionParameter.path_encoding]
        if encoding is not None:
            MotionDetection.remove_background(fulres, bgSubtractor)
            gesture = MotionDetectionParameter.gesture_map[encoding]
            font_size = fulres.shape[0]/750
            cv2.putText(fulres, "Gesture" + ": " + gesture,
                                (40, 100), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0,255,0), 1)
        tasks.put(api.CameraWorkerTask(fulres, img_processor=None))
        return all_centroids, count, params, selected_param

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
            params[MotionDetectionParameter.path], params[MotionDetectionParameter.angle], params[MotionDetectionParameter.path_encoding] = MotionDetection.get_fitted_path_stat(fulres, fitted_line)
            gesture = MotionDetectionParameter.gesture_map[params[MotionDetectionParameter.path_encoding]]
            data = args["active"] + '|' + gesture
            print(data)
            try:
                requests.post(url=url, data=data, timeout=2)
            except Exception:
                print(gesture)
            args["active"] = None
    tasks.put(api.CameraWorkerTask(foreground,
                                   img_processor=show_camera_output,
                                   object_centroid=object_centroid,
                                   all_centroids=all_centroids,
                                   fitted_line=fitted_line,
                                   selected_param=selected_param,
                                   params=params))
    params[MotionDetectionParameter.fps] = int(1 / (time.time() - stime))
    return all_centroids, count, params, selected_param

# camera.start_processing(processing_func, update_func, persistent_args)

wordDetector.run(camera, processing_func, update_func, persistent_args)

# mic = api.Microphone()
# print("Recording")
# start = time.time()
# audio = mic.listen(2)
# print("Done")
# mic.recognize()
# print("It took: " + str(time.time() - start))
# mic.close()
