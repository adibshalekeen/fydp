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

def processing(fulres, bgSubtractor, all_centroids, count, params, selected_param, tasks):
    downresScale = 2
    stime = time.time()
    md = image_processing.MotionDetection
    mdp = image_processing.MotionDetectionParameter

    frame = md.downResImage(fulres, downresScale)
    ###################################################################
    foreground, object_centroid = md.process_image_contours(
        frame, bgSubtractor, downresScale)

    #frame_output = frame.copy()

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
            try:
                requests.post(url=url, data=gesture + "|555")
            except Exception:
                print("Victor done goofed")
            print(params)

    tasks.put(api.CameraWorkerTask(fulres,
                                   img_processor=show_camera_output,
                                   object_centroid=object_centroid,
                                   all_centroids=all_centroids,
                                   fitted_line=fitted_line,
                                   selected_param=selected_param,
                                   params=params))

    # frame_output = md.add_frame_centroid(
    #     object_centroid, frame_output, (255, 255, 255))
    # md.add_frame_path_centroid(all_centroids, frame_output, (255, 255, 255))
    # md.draw_fitted_path(frame_output, fitted_line)
    # #output = md.make_visual_output(True, frame_output)
    # md.showconfig(frame_output, selected_param, params)
    # cv2.imshow("output", frame_output)
    
   
    #################################################################

    # # if the `q` key is pressed, break from the loop
    # key = cv2.waitKey(1) & 0xFF
    # if key == ord('1'):
    #     selected_param = mdp.timeout
    # if key == ord('2'):
    #     selected_param = mdp.max_len
    # if key == ord('3'):
    #     selected_param = mdp.min_len
    # if key == ord('='):
    #     params[selected_param] += 1
    # if key == ord('-'):
    #     params[selected_param] -= 1

    params[mdp.fps] = int(1 / (time.time() - stime))
    print('FPS {:.1f}'.format(1 / (time.time() - stime)))
    return all_centroids, count, params, selected_param

camera.start_processing(processing, delta=True)
