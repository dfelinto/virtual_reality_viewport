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

    @property
    def texture(self):
        print(self._fbo._gl_data.color_tex)
        return self._fbo._gl_data.color_tex

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
        self._fbo = FBO()

        self._width = 512
        self._height = 512

        return True

    def loop(self):
        """
        Get fresh tracking data
        """
        print_debug('loop()')

    def frameReady(self):
        """
        The frame is ready to be send to the device
        """
        self._fbo.run()
        print_debug('frameReady()')

    def quit(self):
        """
        Garbage collection
        """
        self._fbo.delete()
        print_debug('quit()')

from bgl import *


global _time
_time = 0

# ##################
# Data struct
# ##################

class GLdata:
    def __init__(self):
        self.color_tex = -1
        self.fb = -1
        self.rb = -1
        self.size = 0


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


def view_reset(viewport):
    # Get texture info
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_TEXTURE)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glViewport(viewport[0], viewport[1], viewport[2], viewport[3])


# ##################
# FBO related routines
# ##################

class FBO:
    __slots__ = {
            "_gl_data",
            }

    def __init__(self):

        # initialize opengl data
        self._gl_data = GLdata()

        # initialize fbo
        self.setup()


    def setup(self):
        gl_data = self._gl_data
        gl_data.size = 128
        size = gl_data.size

        id_buf = Buffer(GL_INT, 1)

        act_fbo = Buffer(GL_INT, 1)
        glGetIntegerv(GL_FRAMEBUFFER, act_fbo)

        act_tex = Buffer(GL_INT, 1)
        glGetIntegerv(GL_ACTIVE_TEXTURE, act_tex)

        #RGBA8 2D texture, 24 bit depth texture, sizexsize
        glGenTextures(1, id_buf)
        gl_data.color_tex = id_buf.to_list()[0]

        glBindTexture(GL_TEXTURE_2D, gl_data.color_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        # NULL means reserve texture memory, but texels are undefined
        null_buffer = Buffer(GL_BYTE, [(size + 1) * (size + 1) * 4])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, size, size, 0, GL_BGRA, GL_UNSIGNED_BYTE, null_buffer)

        glBindTexture(GL_TEXTURE_2D, act_tex[0])

        glGenFramebuffers(1, id_buf)
        gl_data.fb = id_buf.to_list()[0]
        glBindFramebuffer(GL_FRAMEBUFFER, gl_data.fb)

        # Attach 2D texture to this FBO
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, gl_data.color_tex, 0)

        glGenRenderbuffers(1, id_buf)
        gl_data.depth_rb = id_buf.to_list()[0]
        glBindRenderbuffer(GL_RENDERBUFFER, gl_data.depth_rb)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, size, size)

        # Attach depth buffer to FBO
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, gl_data.depth_rb)

        # Does the GPU support current FBO configuration?
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)

        glBindFramebuffer(GL_FRAMEBUFFER, act_fbo[0])

        if status == GL_FRAMEBUFFER_COMPLETE:
            print("FBO: good: {0} : {1} : {2}".format(gl_data.color_tex, gl_data.depth_rb, gl_data.fb))
        else:
            print("FBO: error", status)


    def run(self):
        """
        draw in the FBO
        """
        gl_data = self._gl_data

        act_fbo = Buffer(GL_INT, 1)
        glGetIntegerv(GL_FRAMEBUFFER, act_fbo)

        # setup
        viewport = Buffer(GL_INT, 4)
        glGetIntegerv(GL_VIEWPORT, viewport)
        glViewport(0, 0, gl_data.size, gl_data.size)

        glBindFramebuffer(GL_FRAMEBUFFER, gl_data.fb)
        glActiveTexture(GL_TEXTURE0)

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        act_tex = Buffer(GL_INT, 1)
        glGetIntegerv(GL_ACTIVE_TEXTURE, act_tex)

        glDisable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # actual drawing
        view_setup()

        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, gl_data.color_tex)

        # actual drawing
        self._draw_a_quad()

        glBindTexture(GL_TEXTURE_2D, act_tex[0])

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)

        view_reset(viewport)

        # unbinding
        glBindFramebuffer(GL_FRAMEBUFFER, act_fbo[0])

        glViewport(viewport[0], viewport[1], viewport[2], viewport[3])

    def _draw_a_quad(self):
        """
        draw an animated quad on the screen
        """
        import time
        import math

        global _time

        speed = 0.01

        one = 1.0
        zer = 0.0

        _time, _int = math.modf(_time + speed)
        factor = _time * 2.0

        if factor > 1.0:
            factor = 2.0 - factor;

        one = one - factor;
        zer = factor - zer;

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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

    def visualize(self):
        """
        draw the FBO in a quad
        """
        gl_data = self._gl_data

        current_color = Buffer(GL_FLOAT, 4)
        glGetFloatv(GL_CURRENT_COLOR, current_color);

        act_tex = Buffer(GL_INT, 1)
        glGetIntegerv(GL_ACTIVE_TEXTURE, act_tex)

        viewport = Buffer(GL_INT, 4)
        glGetIntegerv(GL_VIEWPORT, viewport)
        glViewport(300, 200, 256, 256)
        glScissor(300, 200, 256, 256)

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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
        gluLookAt(0.0, 0.0, 1.0,0.0,0.0, 0.0, 0.0,1.0,0.0)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, gl_data.color_tex)

        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord3f(1.0, 1.0, 0.0)
        glVertex2f( 1.0, 1.0)
        glTexCoord3f(0.0, 1.0, 0.0)
        glVertex2f(-1.0, 1.0)
        glTexCoord3f(0.0, 0.0, 0.0)
        glVertex2f(-1.0,-1.0)
        glTexCoord3f(1.0, 0.0, 0.0)
        glVertex2f( 1.0,-1.0)
        glEnd()

        glColor4fv(current_color)

        glDisable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, act_tex[0])

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glMatrixMode(GL_TEXTURE)
        glPopMatrix()

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        glViewport(viewport[0], viewport[1], viewport[2], viewport[3])
        glScissor(viewport[0], viewport[1], viewport[2], viewport[3])

    def _debug_quad(self):
        viewport = Buffer(GL_INT, 4)
        glGetIntegerv(GL_VIEWPORT, viewport)
        glViewport(300, 200, 256, 256)
        glScissor(300, 200, 256, 256)

        # actual drawing
        self._draw_a_quad()

        glViewport(viewport[0], viewport[1], viewport[2], viewport[3])
        glScissor(viewport[0], viewport[1], viewport[2], viewport[3])

    def delete(self):
        """
        cleanup FBO data
        """
        gl_data = self._gl_data
        id_buf = Buffer(GL_INT, 1)

        id_buf.to_list()[0] = gl_data.color_tex
        glDeleteTextures(1, id_buf)

        id_buf.to_list()[0] = gl_data.depth_rb
        glDeleteRenderbuffers(1, id_buf)

        id_buf.to_list()[0] = gl_data.fb
        glDeleteFramebuffers(1, id_buf)

    def __del__(self):
        self.delete()

