import bpy

from bpy.app.handlers import persistent

TODO = True

from .preview import Preview
from .hmd import HMD


# ############################################################
# Util Functions
# ############################################################

def getAddonName():
    return __name__.split('.')[0]


def getDisplayBackend(context):
    """preference set in the addon"""
    addon = getAddonName()
    preferences = context.user_preferences.addons[addon].preferences
    return preferences.display_backend


# ############################################################
# Main Operator
# ############################################################

class VirtualRealityDisplayOperator(bpy.types.Operator):
    """"""
    bl_idname = "view3d.virtual_reality_display"
    bl_label = "Toggle Virtual Reality Display"
    bl_description = ""

    _gl_data = None
    _timer = None
    _handle = None
    _width = 1920
    _height = 1080

    action = bpy.props.EnumProperty(
        description="",
        items=(("ENABLE", "Enable", "Enable"),
               ("DISABLE", "Disable", "Disable"),
               ),
        default="DISABLE",
        options={'SKIP_SAVE'},
        )

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def modal(self, context, event):
        wm = context.window_manager
        vr = wm.virtual_reality

        if not vr.is_enabled:
            self._quit(context)
            context.area.tag_redraw()
            return {'FINISHED'}

        if event.type == 'TIMER':
            self.loop()

            if vr.use_preview:
                context.area.tag_redraw()

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        wm = context.window_manager
        vr = wm.virtual_reality

        is_enabled = vr.is_enabled

        if self.action == 'DISABLE':
            if vr.is_enabled:
                self.quit(context)
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Virtual Reality Display is not enabled")
                return {'CANCELLED'}

        else: # ENABLE
            if vr.is_enabled:
                self.report({'ERROR'}, "Virtual Reality Display is already enabled")
                return {'CANCELLED'}

            if self.init(context):
                return {'RUNNING_MODAL'}
            else:
                # quit right away
                self._quit(context)
                self.report({'ERROR'}, "Error initializing device")

        return {'CANCELLED'}

    def quit(self, context):
        """garbage collect"""
        # change it so the original modal operator will clean things up
        wm = context.window_manager
        wm.virtual_reality.is_enabled = False

    def _quit(self, context):
        """actual quit"""
        wm = context.window_manager

        if self._timer:
            wm.event_timer_remove(self._timer)
            del self._timer

        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            del self._handle

        self._hmd.quit()
        self._preview.quit()

    def init(self, context):
        """
        Initialize the callbacks and the external devices
        """
        wm = context.window_manager
        wm.virtual_reality.is_enabled = True

        # setup modal
        self._timer = wm.event_timer_add(1.0 / 75.0, context.window) # 75 Hz
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self._draw_callback_px, (context,), 'WINDOW', 'POST_PIXEL')
        wm.modal_handler_add(self)

        display_backend = getDisplayBackend(context)
        self._hmd = HMD(display_backend)
        self._preview = Preview()

        if self._hmd.isConnected():
            if self._hmd.init():
                # get the data from device
                width = self._hmd.width
                height = self._hmd.height
                texture = self._hmd.texture

                self._preview.init(width, height, texture)

                return True

        return False

    def loop(self):
        """
        Get fresh tracking data and render into the FBO
        """
        self._hmd.loop()

        fbo = self._hmd.fbo
        width = self._hmd.width
        height = self._hmd.height
        projection_matrix = self._hmd.projection_matrix
        modelview_matrix = self._hmd.modelview_matrix

        TODO
        """
        bpy.ops.view3d.offscreen(fbo, width, height, projection_matrix, modelview_matrix)
        """

        self._hmd.frameReady()

    def _draw_callback_px(self, context):
        """callback function, run every time the viewport is refreshed"""
        self._preview.loop()


# ############################################################
# Global Properties
# ############################################################

class VirtualRealityInfo(bpy.types.PropertyGroup):
    is_enabled = bpy.props.BoolProperty(
            name="Enabled",
            default=False,
            )

    use_preview = bpy.props.BoolProperty(
            name="Preview",
            default=False,
            )

# ############################################################
# Callbacks
# ############################################################

@persistent
def virtual_reality_load_pre(dummy):
    wm = bpy.context.window_manager
    wm.virtual_reality.is_enabled = False


@persistent
def virtual_reality_load_post(dummy):
    wm = bpy.context.window_manager
    wm.virtual_reality.is_enabled = False


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.app.handlers.load_pre.append(virtual_reality_load_pre)
    bpy.app.handlers.load_pre.append(virtual_reality_load_post)

    bpy.utils.register_class(VirtualRealityDisplayOperator)
    bpy.utils.register_class(VirtualRealityInfo)
    bpy.types.WindowManager.virtual_reality = bpy.props.PointerProperty(
            name="virtual_reality",
            type=VirtualRealityInfo,
            options={'HIDDEN'},
            )


def unregister():
    bpy.app.handlers.load_pre.remove(virtual_reality_load_pre)
    bpy.app.handlers.load_pre.remove(virtual_reality_load_post)

    bpy.utils.unregister_class(VirtualRealityDisplayOperator)
    del bpy.types.WindowManager.virtual_reality
    bpy.utils.unregister_class(VirtualRealityInfo)

