#!/usr/bin/env python3
"""Karthikk 2.0 Audio handler"""
import re
import signal
import os
import random
import time
from glob import glob
from threading import Thread
import snowboydecoder
from flite import flite
from fallback_audio_cb import FallbackCallbackHandler

TOP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESOURCE_FILE = os.path.join(TOP_DIR, "resources/common.res")

SAYINGS = [
    "Sure.One second",
    "Let me check on that",
    "I can help with that",
    ]

QUERIES = [
    " wants to know,",
    " asked,",
    "is wondering",
    ]


class HandleUser:
    """Handler for each user."""

    def __init__(self, user, sayings, queries, cbhandler):
        self.user = user
        self.sayings = sayings
        self.queries = queries
        self.cbhandler = cbhandler
        self.user_wav = flite("Hey {}".format(user))

    def callback(self):
        """Heard user."""
        self.cbhandler.set_user(self.user)

    def ask_user(self, args):
        """Handle recorded audio"""
        fname = args[0]
        from_user = args[1]
        saying = random.choice(self.sayings)
        query = random.choice(self.queries)
        from_wav = flite(from_user)
        message = "Hey {}: {} {} ...".format(
             self.user,
             from_user,
             query[1])
        if saying:
            self.cbhandler.play_audio(saying[0], saying[1])
            time.sleep(0.5)
        self.cbhandler.play_audio(
            [self.user_wav,
             from_wav,
             query[0],
             fname],
            message)

def _get_models(model_dir):
    """Get list of pmdl files."""
    models = []
    files = glob("{}/*.pmdl".format(model_dir))
    for pmdl in files:
        name = re.search(r'/([^/]+)\.pmdl$', pmdl).group(1)
        models.append((name, pmdl))
    #print("Found Models: " + str(models))
    return models

class AudioThread(Thread):
    """audio thread"""
    def __init__(self, handler):
        Thread.__init__(self)
        self.handler = handler or FallbackCallbackHandler()
        self.interrupt = False

        model_dir = os.path.join(TOP_DIR, "models")
        sensitivity = 0.38

        sayings = [[flite(_msg), _msg] for _msg in SAYINGS]
        sayings.append(None) # Allow for no saying

        queries = [[flite(_msg), _msg] for _msg in QUERIES]

        signal.signal(signal.SIGINT, self.handler.signal_handler)
        self.detected_cb = []

        model_map = _get_models(model_dir)
        models = [model[1] for model in model_map]

        for model in model_map:
            user_handler = HandleUser(model[0], sayings, queries, handler)
            self.handler.add_user(model[0], user_handler.ask_user)
            self.detected_cb.append(user_handler.callback)

        self.detector = snowboydecoder.HotwordDetector(
            models, resource=RESOURCE_FILE, sensitivity=sensitivity)

    def stop(self):
        """Stop and terminate this thread"""
        self.interrupt = True

    def interrupt_cb(self):
        """Abort audio recording loop."""
        return self.interrupt

    def run(self):
        """Main Loop"""
        self.detector.start(
            detected_callback=self.detected_cb,
            audio_recorder_callback=self.handler.audio_recorder_cb,
            interrupt_check=self.interrupt_cb,
            sleep_time=0.01)
        self.detector.terminate()

def handle_audio(handler):
    """Main routine."""
    audio = AudioThread(handler)
    audio.setDaemon(True)
    audio.start()
    return audio

if __name__ == "__main__":
    AUD = AudioThread(None)
    AUD.run()
