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
    glBindTexture(GL_TEXTURE_2D, 0)


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
# Framebuffer Routines
# ##################

def check_framebuffer_status(target):
    status = glCheckFramebufferStatus(target)

    if status ==  GL_FRAMEBUFFER_COMPLETE:
        return True
    elif status == GL_FRAMEBUFFER_UNDEFINED:
        print("framebuffer not complete: GL_FRAMEBUFFER_UNDEFINED - returned if the specified framebuffer is the default read or draw framebuffer, but the default framebuffer does not exist.")
    elif status == GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
        print("framebuffer not complete: GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT - returned if any of the framebuffer attachment points are framebuffer incomplete.")
    elif status == GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
        print("framebuffer not complete: GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT - returned if the framebuffer does not have at least one image attached to it.")
    elif status == GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER:
        print("framebuffer not complete: GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER - returned if the value of GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE is GL_NONE for any color attachment point named by GL_DRAW_BUFFERi.")
    elif status ==  GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER:
        print("framebuffer not complete: GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER - returned if GL_READ_BUFFER is not GL_NONE and the value of GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE is GL_NONE for the color attachment point named by GL_READ_BUFFER.")
    elif status ==  GL_FRAMEBUFFER_UNSUPPORTED:
        print("framebuffer not complete: GL_FRAMEBUFFER_UNSUPPORTED - returned if the combination of internal formats of the attached images violates an implementation-dependent set of restrictions.")
    elif status ==  GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE:
        print("framebuffer not complete: GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE - returned if the value of GL_RENDERBUFFER_SAMPLES is not the same for all attached renderbuffers; if the value of GL_TEXTURE_SAMPLES is the not same for all attached textures; or, if the attached images are a mix of renderbuffers and      textures, the value of GL_RENDERBUFFER_SAMPLES does not match the value of GL_TEXTURE_SAMPLES. also returned if the value of GL_TEXTURE_FIXED_SAMPLE_LOCATIONS i     s not the same for all attached textures; or, if the attached images are a mix of renderbuffers and textures, the value of GL_TEXTURE_FIXED_SAMPLE_LOCATIONS is not GL_TRUE for all attached textures.")
    elif status ==  GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS:
        print("framebuffer not complete: GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS - returned if any framebuffer attachment is layered, and any populated attachment is not layered, or if all populated color attachments are not from textures of the same target.")
    else:
        print("framebuffer not complete: status 0x%x (unknown)" % (status,))

    return False


def create_framebuffer(width, height, target=GL_RGBA):
    """create an empty framebuffer"""
    id_buf = Buffer(GL_INT, 1)

    glGenFramebuffers(1, id_buf)
    fbo_id = id_buf.to_list()[0]

    if fbo_id == 0:
        print("Framebuffer error on creation")
        return -1

    tex_id = create_image(width, height)

    glBindFramebuffer(GL_FRAMEBUFFER, fbo_id)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex_id, 0)

    glGenRenderbuffers(1, id_buf)
    depth_id = id_buf.to_list()[0]

    glBindRenderbuffer(GL_RENDERBUFFER, depth_id)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT32, width, height)

    # attach the depth buffer
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_id)

    #glDrawBuffers(fbo_id, GL_COLOR_ATTACHMENT0)

    if not check_framebuffer_status(GL_DRAW_FRAMEBUFFER):
        delete_framebuffer(fbo_id)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        return -1

    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    return fbo_id


def delete_framebuffer(fbo_id):
    """clear created framebuffer"""
    id_buf = Buffer(GL_INT, 1)
    id_buf.to_list()[0] = fbo_id

    if glIsFramebuffer(fbo_id):
        glDeleteFramebuffers(1, id_buf)

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


def view_reset():
    # Get texture info
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_TEXTURE)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()


def draw_rectangle_rainbow(zed=0.0):
    texco = [(1, 1), (0, 1), (0, 0), (1,0)]
    verco = [(1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), ( 1.0, -1.0)]
    colors = [(1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (1.0, 1.0, 0.0, 0.0)]

    glPolygonMode(GL_FRONT_AND_BACK , GL_FILL)

    glBegin(GL_QUADS)
    for i in range(4):
        color = colors[i]
        glColor4f(color[0], color[1], color[2], color[3])
        glTexCoord3f(texco[i][0], texco[i][1], zed)
        glVertex2f(verco[i][0], verco[i][1])
    glEnd()


def draw_rectangle(zed=0.0):
    texco = [(1, 1), (0, 1), (0, 0), (1,0)]
    verco = [(1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), ( 1.0, -1.0)]

    glPolygonMode(GL_FRONT_AND_BACK , GL_FILL)

    glColor4f(1.0, 1.0, 1.0, 0.0)

    glBegin(GL_QUADS)
    for i in range(4):
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
    view_reset()
    glViewport(self.viewport[0], self.viewport[1], self.viewport[2], self.viewport[3])


    glMatrixMode(GL_MODELVIEW)
    glTranslatef(-cam_pos[0], -cam_pos[1], -cam_pos[2])
