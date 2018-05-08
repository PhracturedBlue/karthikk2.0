#!/usr/bin/env python
"""Karthikk 2.0"""

import queue
import os
import random

import snowboydecoder

import karthikk_audio
import karthikk_visual
import karthikk_faces
import record_wrap
import cats
import cat_gifs
import cat_facts

from operator import itemgetter

class CallbackHandler:
    """Handle callbacks"""

    def __init__(self, main_q, visual_q):
        self.main_q = main_q
        self.visual_q = visual_q
        self.user = None
        self.user_map = {}
        self.faces = []
        facts = cat_facts.FunFacts(self).do_fact
        self.callback_probability = 0.1
        self.callbacks = [
                          cats.Cats(self).do_cats,
                         ]
        self.random_callbacks = [
                          cat_gifs.CatGifs(self).do_cats,
                          facts, facts, facts, facts,
                          facts, facts, facts, facts
                         ]

    def add_user(self, user, callback):
        """Add a user -> callback mapping"""
        self.user_map[user] = callback

    def set_user(self, user):
        """Set current user."""
        self.user = user
        print("Heard {}...".format(self.user))
        #self.set_expression("ShiftyEyes")
        self.visual_q[0].put(["listening", True])

    def signal_handler(self, _signal, _frame):
        """Handle Ctrl-C."""
        os._exit(0)

    def talk(self, state):
        """Set talking state"""
        self.visual_q[0].put(["talk", state])

    def set_expression(self, expression):
        """Set expression"""
        self.visual_q[0].put(["expression", expression])

    def set_message(self, message):
        """Set expression"""
        self.visual_q[0].put(["message", message])

    def run_in_main_thread(self, cmd, *args):
        """Execute command in main thread (non-blocking)"""
        self.main_q.put([cmd, args])

    def audio_recorder_cb(self, fname):
        """Got recorded audio."""
        # This will run in the audio thread
        self.visual_q[0].put(["listening", False])
        if self.callbacks and random.random() < self.callback_probability:
            fname_handler = random.choice(self.callbacks)
        else:
            callbacks = []
            for user in self.user_map:
                if user != self.user:
                    callbacks.append(self.user_map[user].ask_user)
            if not callbacks:
                callbacks.append(self.user_map[self.user].ask_user)
            fname_handler = random.choice(callbacks)
        self.run_in_main_thread(fname_handler, fname, self.user)

    def play_audio_from_main(self, wavs, message):
        self.run_in_main_thread(self.play_audio, wavs, message)

    def lookat(self, pos):
        """Handle camera face detection"""
        if pos:
           pos = sorted(pos, key=itemgetter(0))
           if len(pos) == 1:
               self.visual_q[0].put(["lookat", [pos[0], pos[0]]])
           else:
               self.visual_q[0].put(["lookat", [pos[0], pos[-1]]])
        # else:
        #    self.visual_q[0].put(["lookat", None])
        self.faces = pos

    def update_overlay(self, img):
        """Update overlay image"""
        self.visual_q[0].put(["update_overlay", img])

    def update_counter(self, count):
        """Update counter"""
        self.visual_q[0].put(["update_count", count])

    def visual_exec(self, cmd):
        """Execute command in visual thread and block until complete"""
        print("Executing command")
        self.visual_q[0].put(["exec", cmd])
        self.visual_q[1].get()
        print("Done executing command")

    def key_cb(self, key):
        """Got keypress"""
        print("Key: '{}'".format(key))
        # Note: This function executes in the visual thread
        if key == "q":
            os._exit(0)
        #elif key == "f":
        #    self.visual_q[0].put(["fullscreen", None])
        elif key == "c":
            self.random_event_cb()
        elif key == "r":
            self.run_in_main_thread(record_wrap.run_record, None)
        elif key == "space":
            user = random.choice(list(self.user_map.keys()))
            self.user_map[user].force_recording()

    def random_event_cb(self):
        """Execute a random event"""
        print("Executing random event")
        self.run_in_main_thread(random.choice(self.random_callbacks), None)

    def play_audio(self, *args):
        """Play audio"""
        # This should only be called from one thread at a time
        if len(args) == 1:
            args = args[0]
        wavs = args[0]
        message = args[1]

        if not isinstance(wavs, list):
            wavs = [wavs]

        print("Message: " + message)
        self.set_message(message)
        self.talk(True)

        for wav in wavs:
            print("Wave file: {}".format(wav))
            snowboydecoder.play_audio_file(wav)
        print("Message done")
        self.talk(False)
        self.set_message("")

def main():
    """Main function"""
    visual_q = [queue.Queue(), queue.Queue()]
    main_q = queue.Queue()
    handler = CallbackHandler(main_q, visual_q)
    karthikk_visual.handle_visuals(visual_q, handler.key_cb, handler.random_event_cb)
    karthikk_faces.handle_faces(False, handler)

    audio = karthikk_audio.handle_audio(handler)
    print("Karthikk 2.0 Ready")
    while True:
        cmd, arg = main_q.get()
        # If we get here we need to stop the audio thread, run the cmd, and restart it
        audio.stop()
        audio.join()
        audio = None
        cmd(arg)
        audio = karthikk_audio.handle_audio(handler)

if __name__ == "__main__":
    main()
