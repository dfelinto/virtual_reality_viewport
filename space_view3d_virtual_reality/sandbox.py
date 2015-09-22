import bpy

TODO = True

from .opengl_helper import (
        create_framebuffer,
        delete_framebuffer,
        )


class VirtualRealitySandboxOperator(bpy.types.Operator):
    """"""
    bl_idname = "view3d.virtual_reality_sandbox"
    bl_label = "Toggle Virtual Reality Sandbox"
    bl_description = ""

    _fbo = -1
    _timer = None
    _width = 1920
    _height = 1080

    @classmethod
    def poll(cls, context):
        return True

    def modal(self, context, event):
        if event.type == 'TIMER':
            TODO # update FBO

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        TODO # check if oculus is connected

        if context.area.type == 'VIEW_3D':
            self._timer = context.window_manager.event_timer_add(1.0 / 75.0, context.window) # 75 Hz
            self._init(self._width, self._height)
            return {'MODAL'}

        return {'CANCELLED'}

    def _quit(self):
        """garbage collect"""
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            del self._timer

        if self._fbo != -1:
            delete_framebuffer(self._fbo_id)

    def _init(self, width, height):
        self._fbo = create_framebuffer(width, height


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.utils.register_class(VirtualRealitySandboxOperator)


def unregister():
    bpy.utils.unregister_class(VirtualRealitySandboxOperator)

