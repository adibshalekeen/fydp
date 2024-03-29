from gestures import image_processing
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
from scipy.stats import norm
import numpy as np

downresScale = 3

vs = VideoStream(src=0).start()
time.sleep(2.0)

all_centroids = np.array([[[], []]])
avg_centroid_distance = None
start_dropout = 0.15
end_dropout = 0

count = 10

bgSubtractor = cv2.createBackgroundSubtractorMOG2(history=1)

md = image_processing.MotionDetection
mdp = image_processing.MotionDetectionParameter

params = {
    mdp.fps: 0,
    mdp.timeout: 10,
    mdp.max_len: 70,
    mdp.min_len: 0.25,
    mdp.min_centroid_count: 10,
    mdp.path: (None, None),
    mdp.angle: None,
    mdp.path_encoding: None
}
selected_parameter = mdp.timeout
fitted_line_to_draw = None
gesture = None

while True:
    stime = time.time()
    fulres = vs.read()
    frame = fulres
    frame = md.downResImage(fulres, downresScale)

    foreground, object_centroid = md.process_image_contours(
        frame, bgSubtractor, downresScale)

    # frame_output = fulres.copy()
    frame_output = foreground

    count, all_centroids, avg_centroid_distance = md.add_centroid(
        all_centroids, object_centroid, count, params[mdp.timeout], avg_centroid_distance)

    count, all_centroids, fitted_line, avg_centroid_distance = md.test_path(
        all_centroids,
        count, 
        params[mdp.timeout],
        params[mdp.max_len],
        params[mdp.min_len], 
        params[mdp.min_centroid_count],
        start_dropout,
        end_dropout,
        avg_centroid_distance)

    frame_output = md.add_frame_centroid(object_centroid, frame_output, (255, 255, 255))

    md.add_frame_path_centroid(all_centroids, frame_output, (255, 255, 255))

    if (fitted_line[0] is not None):
        fitted_line_to_draw = fitted_line
        params[mdp.path], params[mdp.angle], params[mdp.path_encoding] = md.get_fitted_path_stat(frame_output, fitted_line)
        gesture = mdp.gesture_map[params[mdp.path_encoding]]
        print(gesture)
    if fitted_line_to_draw is not None:
        md.draw_fitted_path(frame_output, fitted_line_to_draw)
        params[mdp.path], params[mdp.angle], params[mdp.path_encoding] = md.get_fitted_path_stat(frame_output, fitted_line_to_draw)

    output = md.make_visual_output(True, frame_output)
    # md.showconfig(output, selected_parameter, pa
    if gesture is not None:
        color = (0,255,0)
        cv2.putText(output, gesture, (50,100), cv2.FONT_HERSHEY_SIMPLEX, 2, color, thickness=3)
    cv2.namedWindow("output",cv2.WND_PROP_FULLSCREEN)
    cv2.imshow("output", output.astype(np.uint8))

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
vs.stop()
cv2.destroyAllWindows()