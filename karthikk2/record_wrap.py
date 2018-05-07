"""Wrapper to launch recorder"""

import os

TOP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def run_record(_args):
    path = os.path.join(TOP_DIR, "record.py")
    os.system("x-terminal-emulator -e '{}'".format(path))
