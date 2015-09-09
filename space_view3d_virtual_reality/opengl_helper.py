import bpy
from bgl import *
from mathutils import Matrix, Euler

SpaceView3D = bpy.types.SpaceView3D
callback_handle = []


fragment_shader ="""
#version 120
uniform sampler2D color_buffer;

void main(void)
{
    vec2 coords = gl_TexCoord[0].st;
    vec4 foreground = texture2D(color_buffer, coords);
    gl_FragColor = mix(foreground, vec4(1.0, 0.0, 0.0, 1.0), 0.5);
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


def print_program_errors(program):
    """"""
    log = Buffer(GL_BYTE, 1024)
    length = Buffer(GL_INT, 1)

    glGetProgramInfoLog(program, len(log), length, log)

    print("Error in GLSL Program:\n")

    msg = ""
    for i in range(length[0]):
        msg += chr(log[i])

    print (msg)

# ######################
# OpenGL Image Routines
# ######################

def resize(self, context):
    """we can run every frame or only when width/height change"""
    # remove old textures
    self.quit()

    self.width = context.region.width
    self.height = context.region.height

    self.buffer_width, self.buffer_height = calculate_image_size(self.width, self.height)

    # image to dump screen
    self.color_id = create_image(self.buffer_width, self.buffer_height, GL_RGBA)


def calculate_image_size(width, height):
    """get a power of 2 size"""
    buffer_width, buffer_height = 0,0

    i = 0
    while (1 << i) <= width:i+= 1
    buffer_width = 1 << i

    i = 0
    while (1 << i) <= height:i+= 1
    buffer_height = 1 << i

    return buffer_width, buffer_height


def update_image(tex_id, viewport, target=GL_RGBA, texture=GL_TEXTURE0):
    """copy the current buffer to the image"""
    glActiveTexture(texture)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glCopyTexImage2D(GL_TEXTURE_2D, 0, target, viewport[0], viewport[1], viewport[2], viewport[3], 0)


def create_image(width, height, target=GL_RGBA):
    """create an empty image, dimensions pow2"""
    if target == GL_RGBA:
        target, internal_format, dimension  = GL_RGBA, GL_RGB, 3
    else:
        target, internal_format, dimension = GL_DEPTH_COMPONENT32, GL_DEPTH_COMPONENT, 1

    null_buffer = Buffer(GL_BYTE, [(width + 1) * (height + 1) * dimension])

    id_buf = Buffer(GL_INT, 1)
    glGenTextures(1, id_buf)

    tex_id = id_buf.to_list()[0]
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexImage2D(GL_TEXTURE_2D, 0, target, width, height, 0, internal_format, GL_UNSIGNED_BYTE, null_buffer)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    if target == GL_DEPTH_COMPONENT32:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_NONE)

    glCopyTexImage2D(GL_TEXTURE_2D, 0, target, 0, 0, width, height, 0)

    glBindTexture(GL_TEXTURE_2D, 0)

    del null_buffer

    return tex_id


def delete_image(tex_id):
    """clear created image"""
    id_buf = Buffer(GL_INT, 1)
    id_buf.to_list()[0] = tex_id

    if glIsTexture(tex_id):
        glDeleteTextures(1, id_buf)


# ##################
# GLSL Screen Shader
# ##################
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


def setup_uniforms(program, color_id, width, height, is_left):
    """"""
    uniform = glGetUniformLocation(program, "bgl_RenderedTexture")
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, color_id)
    if uniform != -1: glUniform1i(uniform, 0)

    uniform = glGetUniformLocation(program, "bgl_RenderedTextureWidth")
    if uniform != -1: glUniform1f(uniform, width)

    uniform = glGetUniformLocation(program, "bgl_RenderedTextureHeight")
    if uniform != -1: glUniform1f(uniform, height)

    uniform = glGetUniformLocation(program, "bgl_RenderedStereoEye")
    if uniform != -1: glUniform1i(uniform, 0 if is_left else 1)

def bindcode(image):
    """load the image in the graphic card if necessary"""
    image.gl_touch(GL_NEAREST)
    return image.bindcode


# ##################
# Drawing Routines
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


def draw_callback_px(self, context):
    """core function"""
    if not self._enabled: return

    is_left = self.is_stereo_left(context)

    act_tex = Buffer(GL_INT, 1)
    glGetIntegerv(GL_ACTIVE_TEXTURE, act_tex)

    glGetIntegerv(GL_VIEWPORT, self.viewport)

    # (1) dump buffer in texture
    update_image(self.color_id, self.viewport, GL_RGBA, GL_TEXTURE0)

    # (2) run screenshader
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    pjm = Buffer(GL_FLOAT, 16)
    mvm = Buffer(GL_FLOAT, 16)

    cam_pos = context.scene.camera.location.copy()
    glMatrixMode(GL_MODELVIEW)
    glTranslatef(cam_pos[0], cam_pos[1], cam_pos[2])

    glGetFloatv(GL_PROJECTION_MATRIX, pjm)
    glGetFloatv(GL_MODELVIEW_MATRIX, mvm)

    # set identity matrices
    view_setup()

    # update shader
    glUseProgram(self.program_shader)
    setup_uniforms(self.program_shader, self.color_id, self.width, self.height, is_left)
    draw_rectangle()

    # (3) restore opengl defaults
    glUseProgram(0)
    glActiveTexture(act_tex[0])
    glBindTexture(GL_TEXTURE_2D, 0)
    view_reset(self.viewport)

    glMatrixMode(GL_MODELVIEW)
    glTranslatef(-cam_pos[0], -cam_pos[1], -cam_pos[2])
