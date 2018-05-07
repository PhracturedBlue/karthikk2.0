"""Pygame primitives"""

import pygame
import math

MULT = 2
def AAfilledRoundedRect(surface,rect,color,radius=0.4,width=0):

    """
    AAfilledRoundedRect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect         = pygame.Rect(rect)
    color        = pygame.Color(*color)
    alpha        = color.a
    color.a      = 0
    pos          = rect.topleft
    rect.topleft = 0,0
    rectangle    = pygame.Surface(rect.size,pygame.SRCALPHA)

    circle       = pygame.Surface([min(rect.size)*3]*2,pygame.SRCALPHA)
    pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle       = pygame.transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius              = rectangle.blit(circle,(0,0))
    radius.bottomright  = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright     = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft   = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=pygame.BLEND_RGBA_MIN)

    return surface.blit(rectangle,pos)

def AAarc(surface, color, rect, start, end, width=1):
    rect = pygame.Rect(rect)
    color = pygame.Color(*color)
    circle       = pygame.Surface([rect.width*MULT,rect.height*MULT], pygame.SRCALPHA)
    width = MULT*width 
    pygame.draw.arc(circle,color,circle.get_rect(),start, end, width)
    circle       = pygame.transform.smoothscale(circle,rect.size)
    surface.blit(circle, rect.topleft)

def AAellipse(surface, color, rect):
    rect = pygame.Rect(rect)
    color = pygame.Color(*color)
    circle       = pygame.Surface([rect.width*MULT,rect.height*MULT], pygame.SRCALPHA)
    pygame.draw.ellipse(circle,color,circle.get_rect())
    circle       = pygame.transform.smoothscale(circle,rect.size)
    surface.blit(circle, rect.topleft)

# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, font_name=None, aa=False, bkg=None):
    fonts = [ 8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 40, 48, 56, 64, 72 ]
    width = surface.get_width()
    height = surface.get_height()

    index = len(fonts) -1

    while index >= 0:
        words = text.split(' ')
        font = pygame.font.SysFont(font_name, fonts[index])

        fontHeight = font.size("Tg")[1]
        max_lines = int(height / (fontHeight - 2))
        textwid = font.size(text)[0]
        print("Trying font {} # lines {} -- {} <=>{}".format(fonts[index], max_lines, textwid, width))
        if textwid > width:
            # fudge for word boundary
            if textwid / max_lines > width:
                print("    Skipping because {} > {}".format(textwid/max_lines, width))
                index -= 1
                continue
        line = ""
        lastwid = 0
        lines = []
        while words:
            word = words[0]
            templine = line + word + " "
            textwid = font.size(templine)[0]
            if (textwid > width):
                if not line:
                    print("    Skipping because word '{}' doesn't fit on line ({})".format(word, textwid))
                    lines = []
                    break
                lines.append([line, lastwid])
                line = ""
            else:
                words.pop(0)
                line = templine
                lastwid = textwid
        if line:
            lines.append([line, lastwid])
        if not lines or len(lines) > max_lines:
            print("    Skipping because line count is {}".format(len(lines)))
            index -= 1
            continue

        y = int((height - len(lines) * (fontHeight - 2)) / 2.0)
        for line,linewid in lines:
            print("[{},{}] {}".format((width-linewid)/2, y, line))
            img = font.render(line, True, color)
            surface.blit(img, [(width-linewid)/2, y])
            y += fontHeight - 2
        return True
    return False

