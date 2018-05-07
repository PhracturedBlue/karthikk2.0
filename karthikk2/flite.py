"""Flite interface"""
import os
import hashlib

TOP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FLITE = os.path.join(TOP_DIR, "flite", "bin", "flite")
FLITE_VOICE = os.path.join(TOP_DIR, "flite", "voices", "cmu_us_aup.flitevox")

WAV_CACHE_DIR = os.path.join(TOP_DIR, "wav_cache")

def flite(msg):
    md5 = hashlib.md5(msg.encode('utf-8')).hexdigest()
    path = os.path.join(
        WAV_CACHE_DIR, "{}.wav".format(md5))
    if not os.path.exists(path):
        os.system("{} -voice {} -t '{}' /dev/stdout | sox --norm=-3 - {}".format(
            FLITE, FLITE_VOICE, msg, path))
    return path
