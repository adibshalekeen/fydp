from gestures import api
import cv2
import time

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

while True:
    stime = time.time()
    fulres = camera.take_picture()
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
    a_centroid = average_centroid(r_c, g_c, b_c)
    # frame_output = add_centroid(r_c, frame_output, (255,0,0))
    # frame_output = add_centroid(g_c, frame_output, (0,255,0))
    # frame_output = add_centroid(b_c, frame_output, (0,0,255))
    frame_output = add_centroid(a_centroid, frame_output, (255,255,255))
    output = make_visual_output(frame_output, red, green, blue)
    cv2.imshow("output", output.astype(np.uint8))

    if (onlyOnce):
        # if (len(r_c) > 5):
        #   print("image written to file")
        #   cv2.imwrite('sample.jpg', imutils.resize(red, width=500))
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