"""
Debug
=====

Debug device for testing
"""

from . import HMD_Base, HMD_Data

VERBOSE = False

def print_debug(*args):
    if VERBOSE:
        print("Debug: {0}".format(*args))


class Debug(HMD_Base):
    def __init__(self):
        super(Debug, self).__init__('Debug')

    def isConnected(self):
        """
        Check if device is connected

        :return: return True if the device is connected
        :rtype: bool
        """
        print_debug('isConnected()')
        return True

    def init(self):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        print_debug('init()')

        self._width = 1024
        self._height = 512

        return super(Debug, self).init()

    def loop(self):
        """
        Get fresh tracking data
        """
        print_debug('loop()')
        #debug_draw(self._offscreen_object, self._width, self._height)

    def frameReady(self):
        """
        The frame is ready to be send to the device
        """
        print_debug('frameReady()')

    def quit(self):
        """
        Garbage collection
        """
        print_debug('quit()')
        return super(Debug, self).quit()


# ##################
# Debug Debug Debug
# ##################

from bgl import *


global _time
_time = 0


# ##################
# OpenGL generic routines
# ##################

def view_setup():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    glMatrixMode(GL_TEXTURE)
    glPushMatrix()
    glLoadIdentity()

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glOrtho(-1, 1, -1, 1, -20, 20)
    gluLookAt(0.0, 0.0, 1.0, 0.0,0.0,0.0, 0.0,1.0,0.0)


def view_reset():
    # Get texture info
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_TEXTURE)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()


# ##################
# Draw an animated cube on the offscreen object
# ##################

def debug_draw(offscreen_object, width, height):
    """
    draw in the FBO
    """
    import time
    import math
    import gpu

    global _time

    # setup
    viewport = Buffer(GL_INT, 4)
    glGetIntegerv(GL_VIEWPORT, viewport)
    glViewport(0, 0, width, height)

    gpu.offscreen_object_bind(offscreen_object, True)

    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClearDepth(1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glDisable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    view_setup()

    # actual drawing
    speed = 0.01

    one = 1.0
    zer = 0.0

    _time, _int = math.modf(_time + speed)
    factor = _time * 2.0

    if factor > 1.0:
        factor = 2.0 - factor;

    one = one - factor;
    zer = factor - zer;

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(-1.0, 1.0, -1.0, 1.0, 1.0, 20.0)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    gluLookAt(0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    current_color = Buffer(GL_FLOAT, 4)
    glGetFloatv(GL_CURRENT_COLOR, current_color);

    glEnable(GL_COLOR_MATERIAL)

    glBegin(GL_QUADS)
    glColor3f(one, zer, zer)
    glVertex3f(-0.75, -0.75, 0.0)
    glColor3f(zer, one, zer)
    glVertex3f( 0.75, -0.75, 0.0)
    glColor3f(zer, zer, one)
    glVertex3f( 0.75,  0.75, 0.0)
    glColor3f(one, one, zer)
    glVertex3f(-0.75,  0.75, 0.0)
    glEnd()

    glColor4fv(current_color)
    glDisable(GL_COLOR_MATERIAL)

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glDisable(GL_DEPTH_TEST)

    view_reset()
    glViewport(viewport[0], viewport[1], viewport[2], viewport[3])

    # unbinding
    gpu.offscreen_object_unbind(offscreen_object, True)

