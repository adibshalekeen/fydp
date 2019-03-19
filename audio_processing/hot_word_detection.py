import argparse
import os
import platform
import struct
import sys
import time
from datetime import datetime
from threading import Thread

import numpy as np
import pyaudio
import soundfile

sys.path.append(os.path.join(os.path.dirname(__file__), 'binding/python'))

from porcupine import Porcupine

# LIBRARY_PATH =  './libpv_porcupine.so'
# MODEL_FILE_PATH = './porcupine_params.pv'
# KEYWORD_FILE_PATHS = ['./keyword_files/bumblebee_raspberrypi.ppn', './keyword_files/grapefruit_raspberrypi.ppn']

class HotWordDetection(Thread):

    def __init__(
            self,
            library_path,
            model_file_path,
            keyword_file_paths,
            sensitivity=0.5,
            input_device_index=None,
            output_path=None):

        super(HotWordDetection, self).__init__()

        self._library_path = library_path
        self._model_file_path = model_file_path
        self._keyword_file_paths = keyword_file_paths
        self._sensitivity = float(sensitivity)
        self._input_device_index = input_device_index

        self._output_path = output_path
        if self._output_path is not None:
            self._recorded_frames = []

    def run(self, camera, processing_func, update_func, persistent_args):
        """
        Creates an input audio stream, initializes wake word detection (Porcupine) object, and monitors the audio
        stream for occurrences of the wake word(s). It prints the time of detection for each occurrence and index of
        wake word.
        """

        num_keywords = len(self._keyword_file_paths)

        keyword_names =\
            [os.path.basename(x).strip('.ppn').strip('_tiny').split('_')[0] for x in self._keyword_file_paths]

        def _audio_callback(in_data, frame_count, time_info, status):
            if frame_count >= porcupine.frame_length:
                pcm = struct.unpack_from("h" * porcupine.frame_length, in_data)
                result = porcupine.process(pcm)
                if num_keywords == 1 and result:
                    print('[%s] detected keyword' % str(datetime.now()))
                    # add your own code execution here ... it will not block the recognition
                elif num_keywords > 1 and result >= 0:
                    print('[%s] detected %s' % (str(datetime.now()), keyword_names[result]))
                    # or add it here if you use multiple keywords
                    if (persistent_args["active"] is None):
                        persistent_args["active"] = keyword_names[result]

                if self._output_path is not None:
                    self._recorded_frames.append(pcm)
            
            return None, pyaudio.paContinue

        porcupine = None
        pa = None
        audio_stream = None
        sample_rate = None
        try:
            porcupine = Porcupine(
                library_path=self._library_path,
                model_file_path=self._model_file_path,
                keyword_file_paths=self._keyword_file_paths,
                sensitivities=[self._sensitivity] * num_keywords)

            pa = pyaudio.PyAudio()
            sample_rate = porcupine.sample_rate
            num_channels = 1
            audio_format = pyaudio.paInt16
            frame_length = porcupine.frame_length
            
            audio_stream = pa.open(
                rate=sample_rate,
                channels=num_channels,
                format=audio_format,
                input=True,
                frames_per_buffer=frame_length,
                input_device_index=self._input_device_index,
                stream_callback=_audio_callback)

            audio_stream.start_stream()

            # while True:
            #     time.sleep(0.1)
            camera.start_processing(processing_func, update_func, persistent_args)

        except KeyboardInterrupt:
            print('stopping ...')
        finally:
            if audio_stream is not None:
                audio_stream.stop_stream()
                audio_stream.close()

            if pa is not None:
                pa.terminate()

            # delete Porcupine last to avoid segfault in callback.
            if porcupine is not None:
                porcupine.delete()

            if self._output_path is not None and sample_rate is not None and len(self._recorded_frames) > 0:
                recorded_audio = np.concatenate(self._recorded_frames, axis=0).astype(np.int16)
                soundfile.write(self._output_path, recorded_audio, samplerate=sample_rate, subtype='PCM_16')

    _AUDIO_DEVICE_INFO_KEYS = ['index', 'name', 'defaultSampleRate', 'maxInputChannels']

# if __name__ == '__main__':
#     HotWordDetection(
#         library_path=library_path,
#         model_file_path=model_file_path,
#         keyword_file_paths=keyword_file_paths,
#         sensitivity=sensitivities,
#         output_path=None,
#         input_device_index=None
#     ).run()
