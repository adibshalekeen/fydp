from imutils.video import VideoStream
from gestures import image_processing
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
count = 10

bgSubtractor = cv2.createBackgroundSubtractorMOG2(history=1)

md = image_processing.MotionDetection

while True:
	stime = time.time()
	fulres = vs.read()
	frame = fulres
	frame = md.downResImage(fulres, downresScale)

	foreground, object_centroid = md.process_image_contours(frame, bgSubtractor)

	# show the frame and record if the user presses a key
	frame_output = frame.copy()
	count, all_centroids = md.add_centroid(all_centroids, object_centroid, count)
	count, all_centroids, fitted_line = md.test_path(all_centroids, count)
	frame_output = md.add_frame_centroid(object_centroid, frame_output, (255,255,255))
	md.add_frame_path_centroid(all_centroids, frame_output, (255,255,255))
	md.draw_fitted_path(frame_output, fitted_line)
	output = md.make_visual_output(True, frame_output)
	cv2.imshow("output", output.astype(np.uint8))

	# if the `q` key is pressed, break from the loop
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		break

	print('FPS {:.1f}'.format(1 / (time.time() - stime)))

# cleanup the camera and close any open windows
vs.stop()
cv2.destroyAllWindows()