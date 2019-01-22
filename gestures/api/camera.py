from picamera import PiCamera, PiCameraCircularIO
import time

class Camera:
    def __init__(exposure_time, 
                 camera_params,
                 outdir='captures',
                 pic_out_dir='img',
                 vid_out_dir='vid'):
        self._exposure_time = exposure_time
        self._resolution = camera_params["res"]
        self._framerate = camera_params["fps"]
        self._camera = PiCamera(resolution=self._resolution, framerate=self._framerate)
        self._thread = None
        self._pic_out_dir = f'./{outdir}/{pic_out_dir}'
        self._vid_out_dir = f'./{outdir}/{vid_out_dir}'

        # camera module needs some time to warm up after init
        time.sleep(2)

    def take_picture():
        if self._camera is not None:
            self._camera.capture(f'{self._pic_out_dir}/{time.strftime("%m-%d-%H-%M-%S")}.jpg')
    
    def record_video_to_file(recording_time=5, unique_tag=None):
        if self._camera is not None:
            if unique_tag is None:
                unique_tag = time.strftime("%m-%d-%H-%M-%S")
            self._camera.start_recording(f'{self._vid_out_dir}/{unique_tag}.h264')
            self._camera.wait_recording(recording_time)

    def start_recording(handler):
        if self._camera is not None:
            self._thread = new 

    def listen_for_motion(motion_sensor):
        if self._camera is not None:
            stream = PiCameraCircularIO(self._camera, seconds=20)
            camera.start_recording(stream, format='bgr')
            try:
                while True:
                    camera.wait_recording(1)
                    if motion_sensor(stream):
                        self._camera.start_preview()
                        self._camera.wait_recording(5)
                        self._camera.stop_preview()
                        unique_name = f'{self._vid_out_dir}/{timestr}_sample.bgr'
                        stream.copy_to(unique_name)
            finally:
                self._camera.stop_recording()
        return stream, unique_name
    
