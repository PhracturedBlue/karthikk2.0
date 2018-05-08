#!/usr/bin/env python3
"""Karthikk 2.0 Face handler"""

import cv2
import picamera
import io
import os
import numpy
import pygame
import sys
import logging as log
import datetime as dt
from threading import Thread
from time import sleep, clock
from flite import flite

TOP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CASC_PATH = os.path.join(TOP_DIR, "opencv/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml")
log.basicConfig(filename='webcam.log',level=log.INFO)

class FacesThread(Thread):
    """OpenCV thread"""
    def __init__(self, display, handler):
        Thread.__init__(self)
        self.display = display
        self.handler = handler
        self.width = 640
        self.height = 480
        self.faceCascade = cv2.CascadeClassifier(CASC_PATH)

        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.width, self.height)



    def run(self):
        """Main loop."""
        face_count = 0
        last_face_count = 0
        last_change = clock()
        last_date = dt.datetime.today()
        cumulative_faces = 0

        while True:
            stream = io.BytesIO()
            self.camera.capture(stream, format='jpeg')
            # Capture frame-by-frame
            buff = numpy.fromstring(stream.getvalue(), dtype=numpy.uint8)

            #Now creates an OpenCV image
            frame = cv2.imdecode(buff, 1)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = self.faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            # Draw a rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # Display the resulting frame
            resized_image = cv2.resize(frame, (320, 240))

            if face_count != len(faces):
                face_count = len(faces)
                log.info("faces: "+str(len(faces))+" at "+str(dt.datetime.now()))
                last_change = clock()
                
            if self.handler:
                pos = []
                for (x, y, w, h) in faces:
                    pos.append([1.0 - (x+w/2)/self.width, (y+h/2)/self.height])
                self.handler.lookat(pos)
                img = numpy.rot90(resized_image)
                frame = pygame.surfarray.make_surface(img)
                self.handler.update_overlay(frame)

                if dt.datetime.today() != last_date:
                    last_date = dt.datetime.today()
                    cumulative_faces = 0
                    self.handler.update_counter(cumulative_faces)

                if face_count != last_face_count and clock() - last_change > 2:
                    if face_count > last_face_count:
                        cumulative_faces += (face_count + last_face_count)
                        self.handler.update_counter(cumulative_faces)

                    if last_face_count and not face_count:
                        message = "Where did the kitties go?"
                    elif last_face_count > 1 and face_count == 1:
                        message = "Now I only see 1 cat"
                    elif face_count == 1:
                        message = "I see a cat"
                    else:
                        message = "I see {} cats".format(len(faces))
                    wav = flite(message)
                    print("Sending: {}".format(message))
                    #self.handler.play_audio_from_main([wav], message)
                    last_change = clock()
                    last_face_count = face_count

            if self.display:
                cv2.imshow('Video', resized_image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Display the resulting frame
            #cv2.imshow('Video', frame)

        # When everything is done, release the capture
        cv2.destroyAllWindows()

def handle_faces(display=False, handler=None):
    """Main routine."""
    faces = FacesThread(display, handler)
    faces.setDaemon(True)
    faces.start()

if __name__ == "__main__":
    FACES = FacesThread(True, None)
    FACES.run()
