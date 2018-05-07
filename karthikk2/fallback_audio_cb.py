"""Fallback callback-handler when running audio module standalone"""
import random
import os

class FallbackCallbackHandler:
    """Handle callbacks"""

    def __init__(self, callbacks=None):
        self.interrupted = False
        self.user = None
        self.callbacks = callbacks
        self.user_map = {}

    def add_user(self, user, callback):
        """Add a user -> callback mapping"""
        self.user_map[user] = callback

    def set_user(self, user):
        """Set current user."""
        self.user = user
        print("Heard {}...".format(self.user))

    def signal_handler(self, _signal, _frame):
        """Handle Ctrl-C."""
        os._exit(0)

    def talk(self, state):
        """Set talking state"""
        return

    def audio_recorder_cb(self, fname):
        """Got recorded audio."""
        callbacks = list(self.callbacks)
        if len(callbacks) > 1:
            for user in self.user_map:
                if user != self.user:
                    callbacks.append(self.user_map[user])
            fname_handler = random.choice(callbacks)
        else:
            fname_handler = callbacks[0]
        fname_handler(fname)
