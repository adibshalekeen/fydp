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

# frames = []
# firstFrame = None

# md = image_processing.MotionDetection

def processing(frame, prevframe):
    stime = time.time()
    text = "Unoccupied"
    md = image_processing.MotionDetection
    height = frame.shape[1]
    width = frame.shape[0]

    red,r_c,green,g_c,blue,b_c = md.process_image_contours(frame, prevframe)

    # show the frame and record if the user presses a key
    a_centroid = md.average_centroid(r_c, g_c, b_c)
    frame_output = md.add_centroid(a_centroid, frame, (255,255,255))
    #output = md.make_visual_output(frame_output, red, green, blue)
    cv2.imshow("output", frame_output.astype(np.uint8))
    #cv2.imshow("output", frame)
    # if the `q` key is pressed, break from the loop
    key = cv2.waitKey(1) & 0xFF
    print('FPS {:.1f}'.format(1 / (time.time() - stime)))

camera.start_processing(processing, delta=True)
