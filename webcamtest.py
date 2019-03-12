from gestures import image_processing
import argparse
import datetime
import imutils
import time
import cv2
from scipy.stats import norm
import numpy as np

downresScale = 3

vs = cv2.VideoCapture(0)
time.sleep(2.0)

all_centroids = np.array([[[], []]])
count = 10

bgSubtractor = cv2.createBackgroundSubtractorMOG2(history=1)

md = image_processing.MotionDetection
mdp = image_processing.MotionDetectionParameter

params = {
    mdp.fps: 0,
    mdp.timeout: 10,
    mdp.max_len: 70,
    mdp.min_len: 2,
    mdp.path: (None, None),
    mdp.angle: None,
    mdp.path_encoding: None
}
selected_parameter = mdp.timeout

while True:
    stime = time.time()
    fulres = vs.read()[1]
    frame = fulres
    frame = md.downResImage(fulres, downresScale)

    foreground, object_centroid = md.process_image_contours(
        frame, bgSubtractor, downresScale)

    frame_output = fulres.copy()

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
    output = md.make_visual_output(True, frame_output, foreground)
    md.showconfig(output, selected_parameter, params)
    cv2.imshow("output", output.astype(np.uint8))
    if (fitted_line[0] is not None):
        params[mdp.path], params[mdp.angle], params[mdp.path_encoding] = md.get_fitted_path_stat(frame_output, fitted_line)
        print(params[mdp.path_encoding])
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('1'):
        selected_parameter = mdp.timeout
    if key == ord('2'):
        selected_parameter = mdp.max_len
    if key == ord('3'):
        selected_parameter = mdp.min_len
    if key == ord('='):
        params[selected_parameter] += 1
    if key == ord('-'):
        params[selected_parameter] -= 1

    params[mdp.fps] = int(1 / (time.time() - stime))
    # print('FPS {:.1f}'.format(1 / (time.time() - stime)))

# cleanup the camera and close any open windows
vs.release()
cv2.destroyAllWindows()