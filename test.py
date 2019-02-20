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
    "fps":60
}
camera = api.Camera(5,
                    camera_params,
                    process_frame)

frames = []
firstFrame = None

md = image_processing.MotionDetection

while True:
    stime = time.time()
    fulres = camera.take_picture()
    frame = fulres
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
    red,r_c,green,g_c,blue,b_c = md.process_image_contours(frame, firstFrame)

    # show the frame and record if the user presses a key
    frame_output = frame.copy()
    a_centroid = md.average_centroid(r_c, g_c, b_c)
    # frame_output = add_centroid(r_c, frame_output, (255,0,0))
    # frame_output = add_centroid(g_c, frame_output, (0,255,0))
    # frame_output = add_centroid(b_c, frame_output, (0,0,255))
    frame_output = md.add_centroid(a_centroid, frame_output, (255,255,255))
    output = md.make_visual_output(frame_output, red, green, blue)
    cv2.imshow("output", output.astype(np.uint8))

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

cv2.destroyAllWindows()