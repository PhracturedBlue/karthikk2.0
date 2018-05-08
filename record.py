#!/usr/bin/env python3
"""Record a keyword for a given user."""

import collections
import time
import wave
import os
import logging
import contextlib
import sys
import pyaudio
import karthikk2.snowboydetect as snowboydetect

logging.basicConfig()
LOGGER = logging.getLogger("karthikk")
LOGGER.setLevel(logging.INFO)
TOP_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_FILE = os.path.join(TOP_DIR, "resources/common.res")
MODEL_FILE = os.path.join(TOP_DIR, "resources/models/snowboy.umdl")

@contextlib.contextmanager
def ignore_stderr():
    """Prevent pyalsa from spamming stderr."""
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)

class RingBuffer(object):
    """Ring buffer to hold audio from PortAudio"""

    def __init__(self, size=4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        """Adds data to the end of buffer"""
        self._buf.extend(data)

    def get(self):
        """Retrieves data from the beginning of buffer and clears it"""
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp

class RecordSample(object):
    """Record voice class"""

    def __init__(self, decoder_model,
                 resource=RESOURCE_FILE,
                 sensitivity="",
                 audio_gain=1):
        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=resource.encode(), model_str=decoder_model.encode())
        self.detector.SetAudioGain(audio_gain)
        self.audio = None
        self.stream_in = None
        self.recorded_data = []
        if sensitivity:
            self.detector.SetSensitivity(sensitivity.encode())
        self.ring_buffer = RingBuffer(
            self.detector.NumChannels() * self.detector.SampleRate() * 5)

    def listen(self,
               sleep_time=0.03,
               silent_count_threshold=10):
        """Listen for some voice and generate wav file."""

        def _audio_callback(in_data, _frame_count, _time_info, _status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue

        with ignore_stderr():
            self.audio = pyaudio.PyAudio()

        self.stream_in = self.audio.open(
            input=True, output=False,
            format=self.audio.get_format_from_width(
                self.detector.BitsPerSample() / 8),
            channels=self.detector.NumChannels(),
            rate=self.detector.SampleRate(),
            frames_per_buffer=2048,
            stream_callback=_audio_callback)

        state = "WAIT"
        silent_count = 0
        fifo = []
        while True:
            data = self.ring_buffer.get()
            if not data:
                time.sleep(sleep_time)
                continue

            status = self.detector.RunDetection(data)
            if status == -1:
                LOGGER.warning("Error initializing streams or reading audio data")
            #print("{} - {} {}".format(status, silent_count, len(data)))
            #small state machine to handle recording of phrase after keyword
            if state == "WAIT":
                if status != -2:
                    state = "RECORDING"
                    self.recorded_data = []
                    while fifo:
                        self.recorded_data.append(fifo.pop(0))
                    self.recorded_data.append(data)
                    silent_count = 0
                else:
                    fifo.append(data)
                    if len(fifo) > 3:
                        fifo.pop(0)

            elif state == "RECORDING":
                if status == -2:
                    if silent_count > silent_count_threshold:
                        break
                    else:
                        silent_count += 1
                else:
                    silent_count = 0
                    self.recorded_data.append(data)
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()
        return self.save_message()

    def save_message(self):
        """
        Save the message stored in self.recorded_data to a timestamped file.
        """
        filename = 'output' + str(int(time.time())) + '.wav'
        data = b''.join(self.recorded_data)

        #use wave to save data
        wavf = wave.open(filename, 'wb')
        wavf.setnchannels(1)
        wavf.setsampwidth(self.audio.get_sample_size(
            self.audio.get_format_from_width(
                self.detector.BitsPerSample() / 8)))
        wavf.setframerate(self.detector.SampleRate())
        wavf.writeframes(data)
        wavf.close()
        LOGGER.debug("finished saving: %s", filename)
        return filename

def play_audio_file(fname):
    """Play a wav file."""
    ding_wav = wave.open(fname, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    with ignore_stderr():
        audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()

def get_recording(recorder, msg, wav_file):
    """Record a single keyword."""
    while True:
        print(msg)
        tmp_file = recorder.listen()
        play_audio_file(tmp_file)
        yes_no = input("This is what I heard.  Does it sound ok? (y/n/q) ")
        if yes_no.lower() == "y":
            break
        if yes_no.lower() == "q":
            sys.exit(1)
    os.rename(tmp_file, wav_file)

def main(keyword):
    """This is the main application."""
    recorder = RecordSample(MODEL_FILE, sensitivity="0.38")
    name = input("Please type your first name: ")
    if not name:
        return
    wavdir = os.path.join(TOP_DIR, "models/raw", name)
    if os.path.exists(wavdir):
        os.system("/bin/rm {}/*.wav".format(wavdir))
    else:
        os.mkdir(wavdir)
    print("You will need to say '{}' 3 times".format(keyword))
    files = []
    for count in ["1st", "2nd", "3rd"]:
        fname = "{}/{}.wav".format(wavdir, count)
        msg = "{} time: Please say '{}' into the microphone".format(count, keyword)
        get_recording(recorder, msg, fname)
        files.append(fname)

    pmdl = "{}/models/{}.pmdl".format(TOP_DIR, name)
    temp_pmdl = "{}/temp/temp.pmdl".format(TOP_DIR)
    if os.path.exists(temp_pmdl):
        os.unlink(temp_pmdl)
    print("Training model...please wait")
    os.system("python2 {}/train.py {} {} {} {}".format(
        TOP_DIR, files[0], files[1], files[2], temp_pmdl))
    if not os.path.exists(temp_pmdl):
        print("Training failed")
        return
    if os.path.exists(pmdl):
        old_dir = "{}/models/old".format(TOP_DIR)
        if not os.path.exists(old_dir):
            os.mkdir(old_dir)
        idx = 1
        old_file = "{}/{}.pmdl".format(old_dir, name)
        while os.path.exists(old_file):
            old_file = "{}/{}_{}.pmdl".format(old_dir, name, idx)
            idx += 1
        os.rename(pmdl, old_file)
    os.rename(temp_pmdl, pmdl)
        

main("Hey Karthikk")
