import pyaudio
import speech_recognition as sr
import wave

class Microphone:
    def __init__(self, samp_rate=8000, chunk=1024):
        self._audio = pyaudio.PyAudio()
        device_index = -1
        for ii in range(self._audio.get_device_count()):
            if self._audio.get_device_info_by_index(ii).get('name') == "AmazonBsktop Mini Mic: USB Audio (hw:2,0)":
                device_index = ii
        if device_index == -1:
            print("Mic not found")
            return
        self._samp_rate = samp_rate
        self._chunk_size = chunk
        self._form_1 = pyaudio.paInt16
        self._chans = 1
        self._mic = self._audio.open(format = self._form_1,
                               rate = samp_rate,
                               channels=self._chans,
                               input_device_index=device_index,
                               input = True,
                               frames_per_buffer = chunk)
        self._recognizer = sr.Recognizer()

    def listen(self, duration, out="sample.wav"):
        audio_frames = []
        for i in range(0, int((self._samp_rate / self._chunk_size)*duration)):
            data = self._mic.read(self._chunk_size)
            audio_frames.append(data)
        self._mic.stop_stream()

        wavefile = wave.open(out,'wb')
        wavefile.setnchannels(self._chans)
        wavefile.setsampwidth(self._audio.get_sample_size(self._form_1))
        wavefile.setframerate(self._samp_rate)
        wavefile.writeframes(b''.join(audio_frames))
        wavefile.close()
        return audio_frames
    
    def recognize(self):
        audio_file = sr.AudioFile('sample.wav')
        with audio_file as source:
            audio = self._recognizer.record(source)
            try:
                print("You said: " + self._recognizer.recognize_sphinx(audio))
            except sr.UnknownValueError:
                print("Unrecognizible")
            except sr.RequestError as e:
                print("Sphinx error " + str(e))

    def close(self):
        self._mic.close()
        self._audio.terminate()
        