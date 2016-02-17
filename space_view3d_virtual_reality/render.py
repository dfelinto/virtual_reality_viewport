"""
Render Preview Drawing
************************

Rountines to draw an image in an offscreen buffer based
on an equirectangular image and transformation matrices
"""

from .opengl_helper import (
        view_reset,
        view_setup,
        )

from bgl import *

import gpu

class Render:
    def __init__(self):
        self._offscreen = [None, None]
        self._color_texture = [0, 0]

    def init(self, blend_data, scene, area, region):
        """
        """
        width = scene.render.resolution_x
        height = scene.render.resolution_y

        for i in range(2):
            self._offscreen[i] = gpu.offscreen.new(width, height, 0)
            self._color_texture[i] = self._offscreen[i].color_texture

    def quit(self):
        """
        """
        for eye in range(2):
            self._offscreen[eye] = None

    def _drawRectangle(self):
        texco = [(1, 1), (0, 1), (0, 0), (1,0)]
        verco = [(1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), ( 1.0, -1.0)]

        glPolygonMode(GL_FRONT_AND_BACK , GL_FILL)

        glColor4f(1.0, 1.0, 1.0, 0.0)

        glBegin(GL_QUADS)
        for i in range(4):
            glTexCoord3f(texco[i][0], texco[i][1], 0.0)
            glVertex2f(verco[i][0], verco[i][1])
        glEnd()

    def loop(self, eye, offscreen, projection_matrix, modelview_matrix):
        """
        TODO
        """
        if not eye:
            # TODO hack test
            return

        if self._offscreen[eye] is None:
            return

        offscreen.bind()
        # use shader
        # update matrices
        # bind bg texture
        # draw rectangle
        glDisable(GL_DEPTH_TEST)

        view_setup()

        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)

        glBindTexture(GL_TEXTURE_2D, self._color_texture[eye])
        self._drawRectangle()

        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)

        view_reset()
        offscreen.unbind()
