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


fragment_shader ="""
#version 120
uniform sampler2D texture_buffer;
uniform mat4 projectionmodelviewinverse;
uniform int eye;

#define PI  3.14159265

vec3 glUnprojectGL(vec2 coords)
{
    float u = coords.s * 2.0 - 1.0;
    float v = coords.t * 2.0 - 1.0;

    vec4 view = vec4(u, v, 1.0, 1.0);
    vec4 world = projectionmodelviewinverse * vec4(view.x, view.y, -view.z, 1.0);

    return vec3(world[0] * world[3], world[1] *  world[3], world[2] * world[3]);
}

vec2 equirectangular(vec3 vert)
{
    float theta = asin(vert.z);
    float phi = atan(vert.x, vert.y);

    float u = 0.5 * (phi / PI) + 0.25;
    float v = 0.5 + theta/PI;

    return vec2(u,v);
}

void main(void)
{
    vec2 coords = gl_TexCoord[0].st;
    vec3 world = glUnprojectGL(coords);
    coords = equirectangular(normalize(world));

    coords.y *= 0.5f;
    coords.y += (1.0f - float(eye)) * 0.5f;

    vec4 background = texture2D(texture_buffer, coords);

    gl_FragColor = background;
}
"""


# ##################
# GLSL Debug
# ##################

def print_shader_errors(shader):
    """"""
    log = Buffer(GL_BYTE, len(fragment_shader))
    length = Buffer(GL_INT, 1)

    print('Shader Code:')
    glGetShaderSource(shader, len(log), length, log)

    line = 1
    msg = "  1 "

    for i in range(length[0]):
        if chr(log[i-1]) == '\n':
            line += 1
            msg += "%3d %s" %(line, chr(log[i]))
        else:
            msg += chr(log[i])

    print(msg)

    glGetShaderInfoLog(shader, len(log), length, log)
    print("Error in GLSL Shader:\n")
    msg = ""
    for i in range(length[0]):
        msg += chr(log[i])

    print (msg)


# ##################
# GLSL Screen Shader
# ##################

def draw_rectangle(zed=0.0):
    texco = [(1, 1), (0, 1), (0, 0), (1,0)]
    verco = [(1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), ( 1.0, -1.0)]

    glPolygonMode(GL_FRONT_AND_BACK , GL_FILL)

    glBegin(GL_QUADS)
    for i in range(4):
        glColor4f(1.0, 1.0, 1.0, 0.0)
        glTexCoord3f(texco[i][0], texco[i][1], zed)
        glVertex2f(verco[i][0], verco[i][1])
    glEnd()


def create_shader(source, program=None, type=GL_FRAGMENT_SHADER):
    """"""
    if program == None:
        program = glCreateProgram()

    shader = glCreateShader(type)
    glShaderSource(shader, source)
    glCompileShader(shader)

    success = Buffer(GL_INT, 1)
    glGetShaderiv(shader, GL_COMPILE_STATUS, success)

    if not success[0]:
        print_shader_errors(shader)
    glAttachShader(program, shader)
    glLinkProgram(program)

    return program


def setup_uniforms(program, texture_id, eye, projectionmodelviewinverse):
    """"""
    uniform = glGetUniformLocation(program, "texture_buffer")
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    if uniform != -1: glUniform1i(uniform, 0)

    uniform = glGetUniformLocation(program, "eye")
    if uniform != -1: glUniform1i(uniform, eye)

    uniform = glGetUniformLocation(program, "projectionmodelviewinverse")
    if uniform != -1: glUniformMatrix4fv(uniform, 1, 0, projectionmodelviewinverse)


# ##################
# Main Routines
# ##################

class Render:
    def __init__(self):
        self._offscreen = None
        self._color_texture = 0
        self._program = 0

    def init(self, blend_data, scene, area, region):
        """
        """
        width = scene.render.resolution_x
        height = scene.render.resolution_y

        self._offscreen = gpu.offscreen.new(width, height, 0)
        self._color_texture = self._offscreen.color_texture

        self._program = create_shader(fragment_shader)

    def quit(self):
        """
        """
        self._offscreen = None
        self._color_texture = 0

        if self._program:
            glDeleteProgram(self._program)
        self._program = 0

    def loop(self, eye, offscreen, projection_matrix, modelview_matrix):
        """
        """
        if self._offscreen is None:
            return

        # bind hmd offscreen buffer
        offscreen.bind()

        # set identity matrices
        glDisable(GL_DEPTH_TEST)
        view_setup()

        modelviewprojinv_matrix = (projection_matrix * modelview_matrix.to_3x3().to_4x4()).inverted()
        modelviewprojinv_mat = Buffer(GL_FLOAT, (4,4), modelviewprojinv_matrix.transposed())

        glUseProgram(self._program)
        setup_uniforms(self._program, self._color_texture, eye, modelviewprojinv_mat)
        draw_rectangle()

        # restore opengl defaults
        glUseProgram(0)
        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
        view_reset()

        # unbind hmd offscreen buffer
        offscreen.unbind()
