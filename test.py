from gestures import api
from gestures import image_processing
import cv2
import time
import numpy as np
import imutils
import requests

first = True
ip = "http://192.168.0.54:"
port = "2081/sendMeMessage"
url = ip + port
http_params = {'gesture': None}
def process_frame(frame):
    if first:
        first_frame = frame
        first = False
    
camera_params = {
    "res":[640, 480],
    "fps":90
}
camera = api.Camera(5,
                    camera_params,
                    process_frame)

def processing(fulres, bgSubtractor, all_centroids, count, params, selected_param):
    downresScale = 2
    stime = time.time()
    md = image_processing.MotionDetection
    mdp = image_processing.MotionDetectionParameter

    frame = md.downResImage(fulres, downresScale)
    ###################################################################
    foreground, object_centroid = md.process_image_contours(
        frame, bgSubtractor, downresScale)

    frame_output = frame.copy()

    count, all_centroids = md.add_centroid(
        all_centroids, object_centroid, count, params[mdp.timeout])

    count, all_centroids, fitted_line = md.test_path(
        all_centroids,
        count, params[mdp.timeout],
        params[mdp.max_len],
        params[mdp.min_len])

    frame_output = md.add_frame_centroid(
        object_centroid, frame_output, (255, 255, 255))
    md.add_frame_path_centroid(all_centroids, frame_output, (255, 255, 255))
    md.draw_fitted_path(frame_output, fitted_line)
    #output = md.make_visual_output(True, frame_output)
    md.showconfig(frame_output, selected_param, params)
    cv2.imshow("output", frame_output)
    
    if (fitted_line[0] is not None):
        params[mdp.path], params[mdp.angle], params[mdp.path_encoding] = md.get_fitted_path_stat(frame_output, fitted_line)
        gesture = mdp.gesture_map[params[mdp.path_encoding]]
        requests.post(url=url, data=gesture + "|555")
        print(params)
    #################################################################

    # if the `q` key is pressed, break from the loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord('1'):
        selected_param = mdp.timeout
    if key == ord('2'):
        selected_param = mdp.max_len
    if key == ord('3'):
        selected_param = mdp.min_len
    if key == ord('='):
        params[selected_param] += 1
    if key == ord('-'):
        params[selected_param] -= 1

    params[mdp.fps] = int(1 / (time.time() - stime))
    print('FPS {:.1f}'.format(1 / (time.time() - stime)))
    return all_centroids, count, params, selected_param

camera.start_processing(processing, delta=True)
