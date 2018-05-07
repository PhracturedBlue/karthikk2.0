"""Display cat pictures"""
import random
import time
import os
from glob import glob
import pygame
import snowboydecoder
from flite import flite

TOP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CAT_DIR = os.path.join(TOP_DIR, "images", "cats")
MSG1 = "Wouldnt you rather look at some cat pictures instead?"
MSG2 = "Now, wasnt that nice?"
WAV1 = flite(MSG1)
WAV2 = flite(MSG2)

def show_cats(scr):
    """Display cats (called from graphics thread)"""
    width, height = scr.get_size()
    images = glob(os.path.join(CAT_DIR, "*.jpg"))
    random.shuffle(images)
    if not images:
        return
    scr.fill(0)
    pygame.display.flip()
    for img in images:
        surface = pygame.image.load(img).convert()
        scr.blit(surface, [random.randint(0, width - 100), random.randint(0, height - 100)])
        pygame.display.flip()
        time.sleep(0.05)
    time.sleep(3)

class Cats:
    """Show cat pictures"""
    def __init__(self, cbhandler):
        self.cbhandler = cbhandler

    def do_cats(self, *args):
        """Talk about cats, and then show some"""
        self.cbhandler.play_audio(WAV1, MSG1)
        time.sleep(0.5)
        self.cbhandler.visual_exec(show_cats)
        self.cbhandler.play_audio(WAV2, MSG2)
