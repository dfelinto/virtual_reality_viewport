"""
Viewport Preview Drawing
************************

Routines to draw in the viewport the result
that is projected in the HMD
"""

from .opengl_helper import (
        view_reset,
        view_setup,
        )

from bgl import *

TODO = True


class Preview:
    __slots__ = {
            "_color_object_left",
            "_color_object_right",
            }

    def init(self, color_object_left, color_object_right):
        """
        Initialize preview window

        :param color_object_left: 2D Texture binding ID (bind to the Framebuffer Object) for left eye
        :type color_object_left: bgl.GLuint
        :param color_object_right: 2D Texture binding ID (bind to the Framebuffer Object) for right eye
        :type color_object_right: bgl.GLuint
        """
        self.update(color_object_left, color_object_right)

    def quit(self):
        """
        Destroy preview window
        """
        pass

    def update(self, color_object_left, color_object_right):
        """
        Update OpenGL binding textures

        :param color_object_left: 2D Texture binding ID (bind to the Framebuffer Object) for left eye
        :type color_object_left: bgl.GLuint
        :param color_object_right: 2D Texture binding ID (bind to the Framebuffer Object) for right eye
        :type color_object_right: bgl.GLuint
        """
        self._color_object_left = color_object_left
        self._color_object_right = color_object_right


    def _drawRectangle(self, eye):
        texco = [(1, 1), (0, 1), (0, 0), (1,0)]
        verco = [[(0.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), ( 0.0, -1.0)],
                 [(1.0, 1.0), ( 0.0, 1.0), ( 0.0, -1.0), ( 1.0, -1.0)]]

        glPolygonMode(GL_FRONT_AND_BACK , GL_FILL)

        glColor4f(1.0, 1.0, 1.0, 0.0)

        glBegin(GL_QUADS)
        for i in range(4):
            glTexCoord3f(texco[i][0], texco[i][1], 0.0)
            glVertex2f(verco[eye][i][0], verco[eye][i][1])
        glEnd()

    def loop(self, scale):
        """
        Draw in the preview window
        """
        if not scale:
            return

        act_tex = Buffer(GL_INT, 1)
        glGetIntegerv(GL_TEXTURE_2D, act_tex)

        if scale != 100:
            viewport = Buffer(GL_INT, 4)
            glGetIntegerv(GL_VIEWPORT, viewport)

            width = int(scale * 0.01 * viewport[2])
            height = int(scale * 0.01 * viewport[3])

            glViewport(viewport[0], viewport[1], width, height)
            glScissor(viewport[0], viewport[1], width, height)

        glDisable(GL_DEPTH_TEST)

        view_setup()

        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)

        glBindTexture(GL_TEXTURE_2D, self._color_object_left)
        self._drawRectangle(0)

        glBindTexture(GL_TEXTURE_2D, self._color_object_right)
        self._drawRectangle(1)

        glBindTexture(GL_TEXTURE_2D, act_tex[0])

        glDisable(GL_TEXTURE_2D)

        view_reset()

        if scale != 100:
            glViewport(viewport[0], viewport[1], viewport[2], viewport[3])
            glScissor(viewport[0], viewport[1], viewport[2], viewport[3])

