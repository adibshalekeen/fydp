from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
from scipy.stats import norm
import numpy as np

width = 281
height = 500

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min_area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

if args.get("video", None) is None:
	vs = VideoStream(src=0).start()
	time.sleep(2.0)
else:
	vs = cv2.VideoCapture(args["video"])

firstFrame = None

imageArray = np.zeros((width * height, 10), dtype=np.uint8)
rv = norm(loc = 0, scale = 1)
x = np.arange(-4, 0, 4 / imageArray.shape[1])
pdf = rv.pdf(x) * 2.5

def process_channel(current, previous, channel):
	# ksize = 3
	# currentBlurred = cv2.GaussianBlur(current, (ksize, ksize), 0)
	# previousBlurred = cv2.GaussianBlur(previous, (ksize, ksize), 0)
	# delta = cv2.absdiff(previousBlurred, currentBlurred)
	delta = cv2.absdiff(previous, current)
	thresh = cv2.threshold(delta, 50, 255, cv2.THRESH_BINARY)[1]
	# thresh = cv2.dilate(thresh, None, iterations=1)
	# thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
	contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# contours1 = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	contours = imutils.grab_contours(contours)
	text = "Unoccupied"

	output = np.zeros((current.shape[0], current.shape[1], 3))
	output[:,:,channel] = thresh

	for c in contours:
		# if the contour is too small, ignore
		# if cv2.contourArea(c) < args["min_area"]:
		if cv2.contourArea(c) < 1000:
			continue
		
		# compute the bounding box for the contour, draw it on the frame
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Occupied"

	cv2.putText(output, "Room Status: {}".format(text), (10, 20), 
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(output, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, output.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	return output

def process_image(frame, previousFrame):
	red = process_channel(frame[:,:,0], previousFrame[:,:,0], 0)
	green = process_channel(frame[:,:,1],previousFrame[:,:,1], 1)
	blue = process_channel(frame[:,:,2],previousFrame[:,:,2], 2)
	return red, green, blue

while True:
	stime = time.time()
	frame = vs.read()
	frame = frame if args.get("video", None) is None else frame[1]
	text = "Unoccupied"

	# if the frame could not be grabbed, then we have reached the end of the video
	if frame is None: 
		break

	# resize the frame, convert it to grayscale and blur it
	frame = imutils.resize(frame, width=500)

	# if the first frame is None, initialize it
	if firstFrame is None:
		firstFrame = frame
		continue

	red, green, blue = process_image(frame, firstFrame)

	# show the frame and record if the user presses a key
	output = np.zeros((width * 2, height * 2, 3))
	output[0:width, 0:height] = frame
	output[0:width, height:2*height, :] = red
	output[width:2*width, 0:height, :] = green
	output[width:2*width, height:2*height, :] = blue
	cv2.imshow("output", output.astype(np.uint8))

	# if the `q` key is pressed, break from the loop
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		break

	# imageArray = np.roll(imageArray, -1, axis=1)
	# imageArray[:, imageArray.shape[1] - 1] = gray.reshape(width * height)	
	# firstFrame = imageArray.dot(pdf).reshape((width, height)).astype(np.uint8)

	firstFrame = frame
	print('FPS {:.1f}'.format(1 / (time.time() - stime)))

# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()




