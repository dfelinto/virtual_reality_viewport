import bpy

TODO = True

from .opengl_helper import (
        create_framebuffer,
        delete_framebuffer,
        draw_rectangle,
        view_setup,
        )

from bgl import *

class VirtualRealitySandboxOperator(bpy.types.Operator):
    """"""
    bl_idname = "view3d.virtual_reality_sandbox"
    bl_label = "Toggle Virtual Reality Sandbox"
    bl_description = ""

    _fbo = -1
    _timer = None
    _handle = None
    _width = 1920
    _height = 1080

    @classmethod
    def poll(cls, context):
        return True

    def modal(self, context, event):
        if event.type == 'TIMER':
            TODO # update FBO
            print(self._fbo)

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        TODO # check if oculus is connected

        if context.area.type == 'VIEW_3D':
            self._timer = context.window_manager.event_timer_add(1.0 / 75.0, context.window) # 75 Hz
            self._handle = bpy.types.SpaceView3D.draw_handler_add(self._draw_callback_px, (self, context), 'WINDOW', 'POST_VIEW')
            self._init(self._width, self._height)
            return {'RUNNING_MODAL'}

        return {'CANCELLED'}

    def _quit(self):
        """garbage collect"""
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            del self._timer

        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            del self._handle

        if self._fbo != -1:
            delete_framebuffer(self._fbo_id)

    def _init(self, width, height):
        TODO #everything oculus related
        # self._fbo = create_framebuffer(width, height)

        #self._testing_fbo()

    def _testing_fbo(self):
        id_buf = Buffer(GL_INT, 1)

        #RGBA8 2D texture, 24 bit depth texture, 256x256
        glGenTextures(1, id_buf)
        color_tex = id_buf.to_list()[0]

        glBindTexture(GL_TEXTURE_2D, color_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        # NULL means reserve texture memory, but texels are undefined
        null_buffer = Buffer(GL_BYTE, [(256 + 1) * (256 + 1) * 4])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 256, 256, 0, GL_BGRA, GL_UNSIGNED_BYTE, null_buffer)

        #-------------------------
        glGenFramebuffers(1, id_buf)
        fb = id_buf.to_list()[0]
        glBindFramebuffer(GL_FRAMEBUFFER, fb)

        # Attach 2D texture to this FBO
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color_tex, 0)

        # -------------------------
        glGenRenderbuffers(1, id_buf)
        depth_rb = id_buf.to_list()[0]
        glBindRenderbuffer(GL_RENDERBUFFER, depth_rb)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, 256, 256)

        # -------------------------
        # Attach depth buffer to FBO
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_rb)

        # -------------------------
        # Does the GPU support current FBO configuration?
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)

        if status == GL_FRAMEBUFFER_COMPLETE:
            print("FBO: good")
        else:
            print("FBO: error", status)
            return

        # -------------------------
        # and now you can render to GL_TEXTURE_2D
        glBindFramebuffer(GL_FRAMEBUFFER, fb)
        glClearColor(1.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # -------------------------
        glViewport(0, 0, 256, 256)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, 256.0, 0.0, 256.0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # -------------------------
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

        # -------------------------
        view_setup()
        draw_rectangle(zed=0.0)

        pixels = Buffer(GL_FLOAT, [4])
        #glReadPixels(0, 0, 4, 4, GL_BGRA, GL_UNSIGNED_BYTE, pixels)
        for x in range(10):
            for y in range(10):
                glReadPixels(x * 10, y * 10, 1, 1, GL_BGRA, GL_UNSIGNED_BYTE, pixels)
                print(pixels)

        TODO # THIS is the bit that is not working, or rather, FBO as a whole may not be working

        # pixels 0, 1, 2 should be white
        # pixel 4 should be black
        # ----------------
        # Bind 0, which means render to back buffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)


        # Delete resources
        id_buf.to_list()[0] = color_tex
        glDeleteTextures(1, id_buf)

        id_buf.to_list()[0] = depth_rb
        glDeleteRenderbuffers(1, id_buf)
        # Bind 0, which means render to back buffer, as a result, fb is unbound
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        id_buf.to_list()[0] = fb
        glDeleteFramebuffers(1, id_buf)


    def _draw_callback_px(_self, self, context):
        """core function"""
        self._testing_fbo()
        #view_setup()
        #draw_rectangle()


# ############################################################
# Roadmap
# ############################################################

"""
Testing FBO
===========
get FBO drawing working

* create FBO
* draw to FBO via python
* draw FBO on screen


Testing Oculus
==============
draw FBO to direct mode

* get as far as required for direct mode


Blender FBO Rendering
=====================
test bpy.ops.view3d.offset()

* make sure matrices are correctly taken into account


Final Oculus Implementation
===========================
(https://developer.oculus.com/documentation/pcsdk/latest/concepts/dg-render/)

* obtain eye position
* calculate modelview matrix
* obtain projection matrix
* bpy.ops.view3d.offset()
* submit frame to oculus
"""


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.utils.register_class(VirtualRealitySandboxOperator)


def unregister():
    bpy.utils.unregister_class(VirtualRealitySandboxOperator)

