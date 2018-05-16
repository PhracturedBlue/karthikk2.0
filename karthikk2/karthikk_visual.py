"""Draw Karthikk 2.0 Face"""

import sys
import os
import math
import time
import random
from threading import Thread
import pygame
import primitives

os.environ['SDL_VIDEO_CENTERED'] = '1'

TOP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMAGE_DIR = os.path.join(TOP_DIR, "images")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CONSOLE = (51, 255, 0)  ## Console greeen
DARK_RED = (128, 0, 0)
MEDIUM_GREY = (190, 190, 190)
YELLOW = (255, 255, 0)
# pylint: disable=too-many-function-args

pygame.font.init()
pygame.display.init()

def map_range(val, start1, end1, start2, end2):
    """Map range to new range"""
    val -= 1.0 * start1
    val = val * (start2 - end2) / (start1 - end1)
    val += start2
    return val

class Expression:
    """Base-classfor expressions"""
    def __init__(self, fps, scr):
        self.fps = fps
        self.scr = scr
        self.eyeballx = 0
        self.irisx = 0
        self.irisy = 0
        self.close_lefteye = False
        self.close_righteye = False
        self.eye_mirror = False
        self.tick = 0

    def update(self):
        """Update expression"""
        return False

    def draw_mouth(self):
        """Draw mouth"""
        return False

class ShiftyEyes(Expression):
    """Draw shift-eyes"""
    def update(self):
        """Update expression"""
        sec1 = self.fps / 2
        sec2 = self.fps * 3 / 2
        sec3 = self.fps * 2
        if self.tick >= sec3:
            return False
        if self.tick < sec1:
            self.eyeballx = map_range(self.tick, 0, sec1, 0.0, 1.0)
        elif self.tick < sec2:
            self.eyeballx = map_range(self.tick, sec1, sec2, 1.0, -1.0)
        else:
            self.eyeballx = map_range(self.tick, sec2, sec3, -1.0, 0)
        self.irisx = self.eyeballx
        self.tick += 1
        return True

class GooglyEyes(Expression):
    """Draw googly eyes"""
    def update(self):
        """Update expression"""
        if self.tick >= self.fps * 2:
            return False
        self.eye_mirror = True
        angle = map_range(self.tick, 0, self.fps * 2, 0, 2*math.pi)
        #self.eyeballx = math.cos(angle)
        self.irisx = math.cos(2*angle)
        self.irisy = math.sin(2*angle)
        self.tick += 1
        return True

class CrossEyes(Expression):
    """Display cross-eyed face"""
    def update(self):
        """Update expression"""
        if self.tick >= self.fps * 2:
            return False
        self.eye_mirror = True
        self.eyeballx = 1.0
        self.irisx = math.cos(math.pi/4)
        self.irisy = math.sin(math.pi/4)
        self.tick += 1
        return True

class Wink(Expression):
    """Wink right eye"""
    def update(self):
        """Update expression"""
        if self.tick >= self.fps * 1.5:
            return False
        self.close_righteye = True
        self.tick += 1
        return True

class Whistle(Expression):
    """Whiste expression"""
    def __init__(self, fps, scr):
        super().__init__(fps, scr)
        width, height = scr.get_size()
        self.width = width
        self.height = height
        self.eyeballx = 1.0
        self.irisx = math.cos(-math.pi/4)
        self.irisy = math.sin(-math.pi/4)
        self.note = pygame.image.load(os.path.join(IMAGE_DIR, "note.png"))
        self.mouth = pygame.Surface([width / 16, height / 9], pygame.SRCALPHA)
        primitives.AAellipse(
            self.mouth, BLACK, [0, 0, width / 16, height / 9])

    def update(self):
        "Update expression"
        if self.tick > 5 * self.fps:
            return False
        self.tick += 1
        return True

    def draw_mouth(self):
        self.scr.blit(self.mouth, [7.5 * self.width / 16, 4 * self.height / 9])
        pos = 3 * (self.tick % self.fps / 2)
        self.scr.blit(self.note, [pos + 8.5 * self.width / 16, -pos + 3 * self.height / 9])
        return True

class Face:
    """Draw Karthikk's face."""
    # pylint: disable=too-many-instance-attributes

    def __init__(self, surface, fps, background=MEDIUM_GREY, foreground=BLACK,
                 iris=WHITE, iris2=YELLOW, mouth=DARK_RED):
        """Initialize face attributes."""
        # pylint: disable=too-many-arguments
        self.title = "Karthikk 2.0"
        self.default_message = "Ask me a question by saying 'Hey Karthikk'.  Sometimes I get distracted, so press the space-bar to get my attention.  My eyes will light up if I can hear you"
        self.surface = surface
        self.fps = fps
        self.linewidth = 5
        self.lookat = None
        self.num_mouthpos = int(fps / 4)
        self.background = background
        self.foreground = foreground
        self.iris_color = iris
        self.iris_color2 = iris2
        self.mouth_color = mouth
        self.talking = False
        self.listening = False
        self.blinking = 0
        self.width = None
        self.height = None
        self.X = None # pylint: disable=invalid-name
        self.Y = None # pylint: disable=invalid-name
        self.update_rect = None
        self.lefteye = None
        self.righteye = None
        self.eyeball = None
        self.iris = None
        self.iris2 = None
        self.eyelid = None
        self.closed_eye = None
        self.outline = None
        self.mouth = []
        self.mouthpos = 0
        self.expression = None
        self.last_expression_time = time.clock()
        self.last_message_time = time.clock()
        self.perf = None
        self.full_redraw = True
        self.message = None
        self.message_text = None
        self.show_overlay = True
        self.redraw_overlay = False
        self.overlay = None
        self.redraw_count = False
        self.count = 0
        self._recalculate()

    def _recalculate(self):
        width, height = self.surface.get_size()
        if self.width == width and self.height == height:
            return
        print("Recalculating")
        self.width = width
        self.height = height
        self.X = width / 16.0
        self.Y = height / 9.0
        self.update_rect = [4*self.X, 2*self.Y, 8*self.X,4.3*self.Y+4]
        self._eye()
        self._mouth()
        if self.show_overlay:
            monitor = pygame.display.Info()
            overlay_w = 320 if monitor.current_h >= 800 else 133
            self.message = pygame.Surface([width-self.X - overlay_w, 2*self.Y], pygame.SRCALPHA)
        else:
            self.message = pygame.Surface([width-2*self.X, 2*self.Y], pygame.SRCALPHA)
        self.count_surface = pygame.Surface([100, self.Y], pygame.SRCALPHA)
        self.full_redraw = True
        self.redraw_overlay = True
        self.redraw_count = True

    def _face_outline(self):
        """Build face outline"""
        outline = pygame.Surface([10*self.X, 6*self.Y], pygame.SRCALPHA)
        primitives.AAfilledRoundedRect(
            outline,
            (0, 0, 10*self.X, 6*self.Y),
            self.foreground, 0.2)
        primitives.AAfilledRoundedRect(
            outline,
            (self.linewidth, self.linewidth, 10*self.X-2*self.linewidth, 6*self.Y-2*self.linewidth),
            self.background, 0.2)
        return outline

    def _eye(self):
        """Build eyes"""
        self.lefteye = pygame.Surface([3 * self.X, 2 * self.Y]).convert()
        self.righteye = pygame.Surface([3 * self.X, 2 * self.Y]).convert()
        self.eyelid = pygame.Surface([3 * self.X, self.Y]).convert()
        self.eyelid.fill(self.background)
        primitives.AAarc(self.eyelid, self.foreground,
                         [0, 0, 3 * self.X, 2 * self.Y],
                         0, math.pi, self.linewidth)

        self.closed_eye = pygame.transform.flip(self.eyelid, False, True)

        self.eyeball = pygame.Surface([self.X, 1.9*self.Y], pygame.SRCALPHA)
        primitives.AAellipse(self.eyeball, self.foreground, [0, 0, self.X, 1.9 * self.Y])

        self.iris = pygame.Surface([self.X / 4, self.Y / 4]).convert()
        self.iris.fill(self.foreground)
        primitives.AAellipse(self.iris, self.iris_color, [0, 0, self.X / 4, self.Y / 4])

        self.iris2 = pygame.Surface([self.X / 4, self.Y / 4]).convert()
        self.iris2.fill(self.foreground)
        primitives.AAellipse(self.iris2, self.iris_color2, [0, 0, self.X / 4, self.Y / 4])


    def _mouth(self):
        """Build mouth"""
        self.mouth = []
        freq = 1
        count = self.num_mouthpos
        width = int(4 * self.X)
        base = 3*math.pi * freq / width
        for mag in range(0, count):
            mag = mag * self.Y / count
            surf = pygame.Surface([width / 6 + 8, self.Y + 8], pygame.SRCALPHA).convert_alpha()
            for xpos in range(0, int(width/6)):
                ypos = 4 + int(mag * math.sin(base * xpos))
                pygame.draw.circle(surf, self.mouth_color,
                                   (4 + xpos, ypos), 4)
            self.mouth.append(surf)

    def _build_open_eye(self, eye, eyeball_x, iris_x, iris_y):
        """Create a new surface for a single eye"""
        eyeball_x = map_range(eyeball_x, -1.0, 1.0, 0.5*self.X, 1.5*self.X)
        iris_x = map_range(
            iris_x,
            -1.0, 1.0,
            eyeball_x+(0.375-0.375)*self.X, eyeball_x+(0.375+0.375)*self.X)
        iris_y = map_range(iris_y, -1.0, 1.0, (0.25-.125)*self.Y, (1.75-.125)*self.Y)
        eye.fill(self.background)
        eye.blit(self.eyelid, [0, 0])
        eye.blit(self.eyeball, [eyeball_x, 0.05*self.Y])
        iris = self.iris2 if self.listening else self.iris
        eye.blit(iris, [iris_x, iris_y])

    def _build_open_eyes(self, lookat):
        """Create a new surface for each eyes"""
        if not self.expression:
            eyeball_x = map_range(lookat[0][0], 0, 1.0, -1.0, 1.0)
            iris_x = eyeball_x * 0.7
            iris_y = map_range(lookat[0][1], 0, 1.0, -1.0, 1.0) * 0.7
        else:
            eyeball_x = self.expression.eyeballx
            iris_x = self.expression.irisx
            iris_y = self.expression.irisy
        self._build_open_eye(self.lefteye, eyeball_x, iris_x, iris_y)
        if self.expression and self.expression.eye_mirror:
            self.righteye.blit(pygame.transform.flip(self.lefteye, True, False), [0, 0])
        elif lookat[1] == lookat[0]:
            self.righteye.blit(self.lefteye, [0, 0])
        else:
            eyeball_x = map_range(lookat[1][0], 0, 1.0, -1.0, 1.0)
            iris_x = eyeball_x * 0.7
            iris_y = map_range(lookat[1][1], 0, 1.0, -1.0, 1.0) * 0.7
            self._build_open_eye(self.righteye, eyeball_x, iris_x, iris_y)

    def _draw_mouth(self):
        """Draw mouth."""
        if not self.talking:
            self.mouthpos = 0

        flip = False
        num_pos = self.num_mouthpos - 1
        pos = self.mouthpos
        if pos >= 2 * num_pos:
            flip = True
            pos -= 2 * num_pos
        if pos >= num_pos:
            pos = 2 * num_pos - pos

        if flip:
            surf = self.mouth[pos]
            y_q12 = -4 + 5.3 * self.Y
            y_q34 = -4 + 4.3 * self.Y
        else:
            surf = pygame.transform.flip(self.mouth[pos], False, True)
            y_q12 = -4 + 4.3 * self.Y
            y_q34 = -4 + 5.3 * self.Y
        wid,_hght = surf.get_size()
        wid -= 8
        xpos = ((16 + 6) / 2 - 3) * self.X - 3 * wid - 4
        quad1 = surf
        quad2 = pygame.transform.flip(quad1, True, False)
        quad3 = pygame.transform.flip(quad2, True, True)
        quad4 = pygame.transform.flip(quad3, True, False)
        self.surface.blit(quad1, [0 * wid + xpos, y_q12])
        self.surface.blit(quad2, [1 * wid + xpos, y_q12])
        self.surface.blit(quad3, [2 * wid + xpos, y_q34])
        self.surface.blit(quad4, [3 * wid + xpos, y_q34])
        self.surface.blit(quad1, [4 * wid + xpos, y_q12])
        self.surface.blit(quad2, [5 * wid + xpos, y_q12])

        self.mouthpos = (self.mouthpos + 1) % (4 * (len(self.mouth) - 1))

    def _show_message(self, message):
        """Dispaly message in appropriate font"""
        print("Show message {}x{}\n{}".format(self.message.get_width(), self.message.get_height(), message))
        self.message.fill(self.background)
        if message:
            ret = primitives.drawText(self.message, message, self.foreground)
            print("Returned: {}".format(ret))
        y = 7 * self.Y
        if self.show_overlay:
            x = self.X / 2
        else:
            x = self.X
        self.surface.blit(self.message, [x, y])
        pygame.display.update([x, y, self.message.get_width(), self.message.get_height()])

    def _show_count(self):
        """Dispaly count"""
        print("Show count {}".format(self.count))
        self.count_surface.fill(self.background)
        primitives.drawText(self.count_surface, str(self.count), self.foreground)
        self.surface.blit(self.count_surface,
                          [self.width-self.count_surface.get_width(), 0])
        pygame.display.update([self.width-self.count_surface.get_width(), 0,
                               self.count_surface.get_width(), self.count_surface.get_height()])

    def set_talking(self, talking):
        """Set talling state."""
        self.talking = talking
        self.listening = False

    def set_listening(self, listening):
        """Set listening state"""
        self.listening = listening

    def set_expression(self, expression):
        """Set expression"""
        print("Set Expression")
        self.expression = expression

    def set_lookat(self, lookat):
        """Set look location"""
        self.lookat = lookat

    def set_message(self, message):
        """Set message to display"""
        print("Set Message");
        self.message_text = message

    def update_overlay(self, overlay):
        """Update overlay image"""
        if self.show_overlay:
            self.overlay = overlay
            self.redraw_overlay = True

    def update_count(self, count):
        """Update count"""
        self.count = count
        self.redraw_count = True


    def draw(self):
        """Draw face"""
        self._recalculate()
        if self.full_redraw:
            self.surface.fill(self.background)
            font = pygame.font.SysFont(None, 72)
            title = font.render("Karthikk 2.0", True, self.foreground)
            outline = self._face_outline()
            self.surface.blit(
                title,
                [(self.width - title.get_width()) / 2,
                 (self.Y - title.get_height()) / 2])

            countmsg = pygame.Surface([130, self.Y], pygame.SRCALPHA)
            primitives.drawText(countmsg, "cats id'd today", self.foreground)
            self.surface.blit(
                countmsg,
                [self.width - countmsg.get_width() - self.count_surface.get_width(), 0])

            self.surface.blit(outline, [3*self.X, self.Y])
            pygame.display.flip()
            self.full_redraw = False     
            self.redraw_count = True
            self.last_message_time = time.clock()
        t_start = time.perf_counter()
        pygame.draw.rect(self.surface, self.background, self.update_rect)
        t_bg = time.perf_counter()

        if self.message_text is not None:
            self._show_message(self.message_text)
            if self.message_text:
                self.last_message_time = 0
            else:
                self.last_message_time = time.clock()
            self.message_text = None

        if self.redraw_count:
            self._show_count()
            self.redraw_count = False

        if self.last_message_time and time.clock() - self.last_message_time > 5:
            self._show_message(self.default_message)
            self.last_message_time = 0

        if self.blinking:
            self.surface.blit(self.closed_eye, [4.0*self.X, 3*self.Y]) # Closed left eye
            self.surface.blit(self.closed_eye, [9.0*self.X, 3*self.Y]) # Closed right eye
            self.blinking -= 1
        else:
            if not self.lookat:
                mousex, mousey = pygame.mouse.get_pos()
                mousex = map_range(mousex, 0, self.width, 0.0, 1.0)
                mousey = map_range(mousey, 0, self.height, 0.0, 1.0)
                lookat = [[mousex, mousey], [mousex, mousey]]
            else:
                lookat = self.lookat
            self._build_open_eyes(lookat)
            if self.expression and self.expression.close_lefteye:
                self.surface.blit(self.closed_eye, [4.0*self.X, 3*self.Y]) # Closed left eye
            else:
                self.surface.blit(self.lefteye, [4*self.X, 2*self.Y]) # Left eye

            if self.expression and self.expression.close_righteye:
                self.surface.blit(self.closed_eye, [9.0*self.X, 3*self.Y]) # Closed right eye
            else:
                self.surface.blit(self.righteye, [9*self.X, 2*self.Y]) # Right eye

        t_eye = time.perf_counter()
        if self.talking or not self.expression or not self.expression.draw_mouth():
            self._draw_mouth()
        t_mouth = time.perf_counter()
        self.perf = [t_start, t_bg, t_eye, t_mouth]
        if self.expression:
            if not self.expression.update():
                self.expression = None
                self.last_expression_time = time.clock()
                print("Expression Finished")
        if self.show_overlay and self.overlay and self.redraw_overlay:
            x = self.width - self.overlay.get_width()
            y = self.height - self.overlay.get_height()
            self.surface.blit( self.overlay, [x, y])
            pygame.display.update([x, y, self.overlay.get_width(), self.overlay.get_height()])
            self.redraw_overlay = False

    def show(self, fps=None):
        """Draw face on screen"""
        pygame.display.update(self.update_rect)
        if fps:
            t_end = time.perf_counter()
            print("Background: {:.3f} ms Eyes: {:.3f} ms Mouth: {:.3f} ms Total: {:.3f} ms FPS: {:.3f} ms".format(
                (self.perf[1] - self.perf[0]) * 1000,
                (self.perf[2] - self.perf[0]) * 1000,
                (self.perf[3] - self.perf[0]) * 1000,
                (t_end - self.perf[0]) * 1000,
                fps))
                

class VisualThread(Thread):
    """Pygame Thread"""
    def __init__(self, queue, key_handler=None, random_event_cb=None):
        Thread.__init__(self)
        self.fps = 30
        self.random_event_time = 120
        self.benchmark = False
        #self.benchmark = 1000
        self.queue = queue
        self.key_handler = key_handler
        self.random_event_cb = random_event_cb
        self.face = None
        self.size = [1120, 630]
        self.lookat = None
        self.scr = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        #self.face = Face(self.scr, self.fps, background=(0,0,0),foreground=(51,255,0), iris=(255,255,255))
        self.face = Face(self.scr, self.fps)
        self.face.set_talking(False if self.queue else True)

    def toggle_fullscreen(self):
        if self.scr.get_flags() & pygame.FULLSCREEN:
            self.scr = pygame.display.set_mode(self.size)
        else:
            mode = pygame.display.list_modes()[0]
            self.scr = pygame.display.set_mode(mode, pygame.FULLSCREEN)
        self.face.surface = self.scr
        self.face.set_expression(None)
        #pygame.display.toggle_fullscreen()

    def handle_command(self, cmd):
        """Handle command from main thread"""
        if cmd[0] == "talk":
            self.face.set_talking(cmd[1])
        elif cmd[0] == "fullscreen":
            self.toggle_fullscreen()
        elif cmd[0] == "exec":
            cmd[1](self.scr)
            self.face.full_redraw = True
            self.queue[1].put(True)
        elif cmd[0] == "expression":
            if cmd[1] == "ShiftyEyes":
                exp = ShiftyEyes
            elif cmd[1] == "GooglyEyes":
                exp = GooglyEyes
            elif cmd[1] == "CrossEyes":
                exp = CrossEyes
            elif cmd[1] == "Wink":
                exp = Wink
            else:
                print("Unknown expression {}".format(cmd[1]))
                return
            self.face.set_expression(exp(self.fps, self.scr))
        elif cmd[0] == "listening":
            self.face.set_listening(cmd[1])
        elif cmd[0] == "lookat":
            self.face.set_lookat(cmd[1])
        elif cmd[0] == "message":
            self.face.set_message(cmd[1])
        elif cmd[0] == "update_overlay":
            self.face.update_overlay(cmd[1])
        elif cmd[0] == "update_count":
            self.face.update_count(cmd[1])

    def random_expression(self):
        """Choose a random expression"""
        exp = random.choice([GooglyEyes, CrossEyes, ShiftyEyes, Wink, Whistle])
        self.face.set_expression(exp(self.fps, self.scr))

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_e:
                    self.random_expression()
                elif event.key == pygame.K_t:
                    self.face.talking = not self.face.talking
                elif event.key == pygame.K_i:
                    print("fps: {}".format(self.clock.get_fps()))
                elif event.key == pygame.K_f:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_o:
                    self.face.show_overlay = not self.face.show_overlay
                elif self.key_handler:
                    self.key_handler(pygame.key.name(event.key))

    def run(self):
        """Main Loop."""
        #print("Visual thread: {}".format(current_thread()))
        tick = 1
        while True:
            self.clock.tick(self.fps)
            self.handle_events()
            if self.queue and not self.queue[0].empty():
                self.handle_command(self.queue[0].get())
            fps_t1 = time.clock()
            for _i in range(0, self.benchmark or 1):
                self.face.draw()
                if tick % (8 * self.fps) == 0:
                    self.face.blinking = int(self.fps / 8)
                if not self.face.expression:
                    delta = time.clock() - self.face.last_expression_time
                    if (delta > 120 or
                            (delta > 20 and random.randrange(0, 120 * self.fps) < 4)):
                        self.random_expression()
                if not self.face.talking and not self.face.listening and self.random_event_cb:
                    ok = random.randint(0, int(self.fps * self.random_event_time))
                    if ok == 0:
                        self.random_event_cb()
            fps_t2 = time.clock()
            if self.benchmark and fps_t2 - fps_t1:
                print("fps: {}".format(1000.0 / (fps_t2-fps_t1)))
            if tick % (self.fps * 10) == 0:
                self.face.show(self.clock.get_fps())
            else:
                self.face.show()
            tick += 1


def handle_visuals(queue, key_handler=None, random_event_cb=None):
    """Display face in its own thread"""
    video = VisualThread(queue, key_handler, random_event_cb)
    video.setDaemon(True)
    video.start()

if __name__ == "__main__":
    VIDEO = VisualThread(None, None, None)
    VIDEO.run()
