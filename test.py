from gestures import api
from gestures import image_processing
import cv2
import time
import numpy as np

first = True 
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

def processing(fulres, bgSubtractor, all_centroids, count):
    stime = time.time()
    md = image_processing.MotionDetection

    frame = md.downResImage(fulres, 2)

    foreground, object_centroid = md.process_image_contours(frame, bgSubtractor)

    frame_output = frame.copy()
    count, all_centroids = md.add_centroid(all_centroids, object_centroid, count)
    count, all_centroids, fitted_line = md.test_path(all_centroids, count)
    # drawing current centroid
    frame_output = md.add_frame_centroid(object_centroid, frame_output, (255,255,255))
    # drawing path of centroids
    md.add_frame_path_centroid(all_centroids, frame_output, (255,255,255))
    # drawing fitted path
    md.draw_fitted_path(frame_output, fitted_line)
    output = md.make_visual_output(False, frame_output)
    cv2.imshow("output", output.astype(np.uint8))

    # if the `q` key is pressed, break from the loop
    key = cv2.waitKey(1) & 0xFF
    print('FPS {:.1f}'.format(1 / (time.time() - stime)))

camera.start_processing(processing, delta=True)
