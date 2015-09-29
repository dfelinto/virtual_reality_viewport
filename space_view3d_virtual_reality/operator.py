import bpy

from bpy.app.handlers import persistent

from .hmd import HMD

from .preview import Preview

from .lib import (
        getDisplayBackend,
        )

TODO = True


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
    _area_hash = -1

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
        area = context.area

        if not area:
            self.quit(context)
            self._quit(context)
            return {'FINISHED'}

        if not vr.is_enabled:
            self._quit(context)
            area.tag_redraw()
            return {'FINISHED'}

        if event.type == 'TIMER':
            self.loop(context, vr.color_object_left, vr.color_object_right)

            if vr.preview_scale and context.area:
                area.tag_redraw()

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
                wm.virtual_reality.is_enabled = False
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

        # cleanup viewport
        if context.area:
            context.area.tag_redraw()

    def init(self, context):
        """
        Initialize the callbacks and the external devices
        """
        wm = context.window_manager
        wm.virtual_reality.is_enabled = True

        display_backend = getDisplayBackend(context)
        self._hmd = HMD(display_backend)
        self._preview = Preview()

        if not self._hmd.isConnected():
            return False

        if not self._hmd.init():
            return False

        # get the data from device
        width = self._hmd.width
        height = self._hmd.height

        color_object = [0, 0]
        for i in range(2):
            self._hmd.setEye(i)
            color_object[i] = self._hmd.color_object

        self._preview.init(color_object[0], color_object[1])
        self._area_hash = hash(context.area)

        # setup modal
        self._timer = wm.event_timer_add(1.0 / 75.0, context.window) # 75 Hz
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self._draw_callback_px, (context,), 'WINDOW', 'POST_PIXEL')
        wm.modal_handler_add(self)

        return True

    def loop(self, context, color_object_left, color_object_right):
        """
        Get fresh tracking data and render into the FBO
        """
        self._hmd.loop(context)

        for i in range(2):
            self._hmd.setEye(i)

            offscreen_object = self._hmd.offscreen_object
            modelview_matrix = self._hmd.modelview_matrix
            projection_matrix = self._hmd.projection_matrix

            # drawing
            # bpy.ops.view3d.offscreen(offscreen_object=offscreen_object, projection_matrix=projection_matrix, modelview_matrix=modelview_matrix)
            bpy.ops.view3d.offscreen(projection_matrix=projection_matrix, modelview_matrix=modelview_matrix) #DEBUG

        self._hmd.frameReady()
        self._preview.update(color_object_left, color_object_right) #DEBUG


    def _draw_callback_px(self, context):
        """callback function, run every time the viewport is refreshed"""

        if self._area_hash == hash(context.area):
            wm = context.window_manager
            vr = wm.virtual_reality
            self._preview.loop(vr.preview_scale)


# ############################################################
# Global Properties
# ############################################################

class VirtualRealityInfo(bpy.types.PropertyGroup):
    is_enabled = bpy.props.BoolProperty(
            name="Enabled",
            default=False,
            )

    preview_scale = bpy.props.IntProperty(
            name="Preview Scale",
            min=0,
            max=100,
            default=100,
            subtype='PERCENTAGE',
            )

    color_object_left = bpy.props.IntProperty(
            name="Color Object Left",
            default=0,
            subtype='UNSIGNED',
            )

    color_object_right = bpy.props.IntProperty(
            name="Color Object Right",
            default=0,
            subtype='UNSIGNED',
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

