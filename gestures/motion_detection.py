from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
from scipy.stats import norm
import numpy as np

downresScale = 3

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

def threshold_frame(current, previous, threshold_value = 50):
	# ksize = 3
	# currentBlurred = cv2.GaussianBlur(current, (ksize, ksize), 0)
	# previousBlurred = cv2.GaussianBlur(previous, (ksize, ksize), 0)
	# delta = cv2.absdiff(previousBlurred, currentBlurred)
	delta = cv2.absdiff(current, previous)
	threshold_value = (np.max(delta).astype(np.uint32) / 135)*threshold_value
	print("median: ", np.median(delta), "max: ", np.max(delta), "min: ", np.min(delta))
	image_thresh = cv2.threshold(delta, threshold_value, 255, cv2.THRESH_BINARY)[1]
	# thresh = cv2.dilate(thresh, None, iterations=1)
	# thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
	return image_thresh

def get_full_contours(current, previous, channel):
	thresh = threshold_frame(current, previous, 75)
	output = channel_image(thresh, channel)

	im2, contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
	new_contours = []
	if len(contours) > 0:
		for i in range(0, len(contours)):
			area = cv2.contourArea(contours[i])
			if cv2.contourArea(contours[i]) > (750 / (2 ** (downresScale + 2))):
				new_contours.append(contours[i])
	x = 0
	y = 0
	if (len(new_contours) > 0):
		x, y = centroid_from_contours(new_contours)

	cv2.drawContours(output, new_contours, -1, (0,255,0), 1)
	return output, (x, y)

def get_approx_contours(current, previous, channel):
	thresh = threshold_frame(current, previous)
	contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contours = imutils.grab_contours(contours)

	output = channel_image(thresh, channel)

	filteredContours = []

	for c in contours:
		# if the contour is too small, ignore
		if cv2.contourArea(c) < 1000 / (2 ** (downresScale + 2)):
			continue
		# compute the bounding box for the contour, draw it on the frame
		(x, y, w, h) = cv2.boundingRect(c)
		filteredContours.append(cv2.boundingRect(c))
		# cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)

	return output, filteredContours

def relative_position(frameShape, contours):
	f_h = frameShape[0]
	f_w = frameShape[1]
	i = 0
	while i < len(contours): 
		# (x, y, w, h)
		c = contours[i]
		contours[i] = (c[0]/f_w, c[1]/f_h, c[2]/f_w, c[3]/f_h)
		i = i + 1
	return contours

def centroid_from_contours(contours):
	x_sum = 0
	y_sum = 0
	count = 0
	for c in contours:
		count += c.shape[0]
		sum = np.sum(c, axis=0)
		x_sum += sum[0, 0]
		y_sum += sum[0, 1]
	return int(x_sum / count), int(y_sum / count)
		
def channel_image(frame, channel):
	output = np.zeros((frame.shape[0], frame.shape[1], 3))
	output[:,:,channel] = frame
	return output

def process_approx_image_contours(frame, previousFrame):
	red,r_c = get_approx_contours(frame[:, :, 0], previousFrame[:, :, 0], 0)
	green,g_c = get_approx_contours(frame[:, :, 1], previousFrame[:, :, 1], 1)
	blue,b_c = get_approx_contours(frame[:, :, 2], previousFrame[:, :, 2], 2)
	r_c = relative_position(frame.shape, r_c)
	g_c = relative_position(frame.shape, g_c)
	b_c = relative_position(frame.shape, b_c)
	return red,r_c,green,g_c,blue,b_c

def add_frame_centroid(centroid, frame, color=(0,255,0)):
	x = int(centroid[0])
	y = int(centroid[1])
	if x > 0 and y > 0: 
		cv2.rectangle(frame, (x, y), (x + 10, y + 10), color, 1)
	return frame

def add_frame_path_centroid(centroids, frame, color=(0,255,0)):


def process_image_contours(frame, previousFrame):
	red, r_c = get_full_contours(frame[:, :, 0], previousFrame[:, :, 0], 0)
	green, g_c = get_full_contours(frame[:, :, 1], previousFrame[:, :, 1], 1)
	blue, b_c = get_full_contours(frame[:, :, 2], previousFrame[:, :, 2], 2)

	red = add_frame_centroid(r_c, red)
	green = add_frame_centroid(g_c, green)
	blue = add_frame_centroid(b_c, blue)
	return red, r_c, green, g_c, blue, b_c


def centroid(thresh):
	moment = cv2.moments(thresh)
	if moment["m00"] > 0:
		cx = int(moment["m10"]/moment["m00"])
		cy = int(moment["m01"]/moment["m00"])
		return cx, cy
	return None

def process_image_threshold(frame, previousFrame):
	red = threshold_frame(frame[:,:,0], previousFrame[:,:,0])
	green = threshold_frame(frame[:,:,1],previousFrame[:,:,1])
	blue = threshold_frame(frame[:,:,2],previousFrame[:,:,2])

	r_c = centroid(red)
	g_c = centroid(green)
	b_c = centroid(blue)

	red = channel_image(red, 0)
	if r_c is not None:
		x = int(r_c[0])
		y = int(r_c[1])
		cv2.rectangle(red, (x, y), (x + 5, y + 5), (0, 255, 0), 1)
	green = channel_image(green, 1)
	blue = channel_image(blue, 2)
	return red, green, blue

def downResImage(frame, i): 
	if i == 0:
		return frame
	else:
		return cv2.pyrDown(downResImage(frame, i-1))

def make_visual_output(frame, red, green, blue):
	frame = imutils.resize(frame, width=500)
	red = imutils.resize(red, width=500)
	green = imutils.resize(green, width=500)
	blue = imutils.resize(blue, width=500)
	out_h = red.shape[1]
	out_w = red.shape[0]
	out = np.zeros((out_w * 2, out_h * 2, 3))
	out[0:out_w, 0:out_h] = frame
	out[0:out_w, out_h:2*out_h, :] = red
	out[out_w:2*out_w, 0:out_h, :] = green
	out[out_w:2*out_w, out_h:2*out_h, :] = blue
	return out

def average_centroid(*args):
	if len(args) == 0:
		return 0, 0
	sum_x = 0
	sum_y = 0
	count = 0
	for c in args:
		if c[0] == 0 and c[1] == 0:
			continue
		sum_x += c[0]
		sum_y += c[1]
		count += 1
	if count == 0: 
		return 0, 0
	return int(sum_x / count), int(sum_y / count)

def add_centroid(centroids, centroid):
	centroids.append(centroid)

onlyOnce = True

frames = []
all_centroids = []

while True:
	stime = time.time()
	fulres = vs.read()
	frame = fulres
	frame = downResImage(fulres, downresScale)
	frame = frame if args.get("video", None) is None else frame[1]
	text = "Unoccupied"

	# if the frame could not be grabbed, then we have reached the end of the video
	if frame is None: 
		break

	height = frame.shape[1]
	width = frame.shape[0]

	# frame = imutils.resize(frame, width=500)

	# if the first frame is None, initialize it
	if firstFrame is None:
		firstFrame = frame
		continue

	# red,r_c,green,g_c,blue,b_c = process_approx_image_contours(frame, firstFrame)
	# red, green, blue = process_image_threshold(frame, firstFrame)
	red,r_c,green,g_c,blue,b_c = process_image_contours(frame, firstFrame)

	# show the frame and record if the user presses a key
	frame_output = frame.copy()
	add_centroid(all_centroids, average_centroid(r_c, g_c, b_c))
	frame_output = add_frame_centroid(a_centroid, frame_output, (255,255,255))
	output = make_visual_output(frame_output, red, green, blue)
	cv2.imshow("output", output.astype(np.uint8))

	if (onlyOnce):
		# if (len(r_c) > 5):
		# 	print("image written to file")
		# 	cv2.imwrite('sample.jpg', imutils.resize(red, width=500))
		onlyOnce = False

	# if the `q` key is pressed, break from the loop
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		break

	if (len(frames) < 15):
		frames.append(frame)
	else:
		del frames[0]
		frames.append(frame)
	
	# firstFrame = np.average(frames, axis=0).astype(dtype=np.uint8)

	# imageArray = np.roll(imageArray, -1, axis=1)
	# imageArray[:, imageArray.shape[1] - 1] = gray.reshape(width * height)	
	# firstFrame = imageArray.dot(pdf).reshape((width, height)).astype(np.uint8)

	firstFrame = frame
	print('FPS {:.1f}'.format(1 / (time.time() - stime)))

# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()




