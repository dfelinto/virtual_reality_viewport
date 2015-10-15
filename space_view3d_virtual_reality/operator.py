import bpy

from bpy.app.handlers import persistent

from .hmd import HMD

from .preview import Preview

from .lib import (
        getDisplayBackend,
        )


TODO = False


# ############################################################
# Commands
# ############################################################

class Commands:
    recenter = 'RECENTER'
    test = 'TEST'


# ############################################################
# Main Operator
# ############################################################

class VirtualRealityDisplayOperator(bpy.types.Operator):
    """"""
    bl_idname = "view3d.virtual_reality_display"
    bl_label = "Toggle Virtual Reality Display"
    bl_description = ""

    _hmd = None
    _timer = None
    _handle = None
    _hash_slave = -1
    _hash_master = -1
    _slave_setup = False

    action = bpy.props.EnumProperty(
        description="",
        items=(("ENABLE", "Enable", "Enable"),
               ("DISABLE", "Disable", "Disable"),
               ("TOGGLE", "Toggle", "Toggle"),
               ("RECENTER", "Re-Center", "Re-Center tracking data"),
               ),
        default="TOGGLE",
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

        """
        if event.type == 'TIMER':
            self.loop(context)

            if vr.preview_scale and context.area:
                area.tag_redraw()
        """

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        wm = context.window_manager
        vr = wm.virtual_reality

        is_enabled = vr.is_enabled

        if self.action == 'TOGGLE':
            self.action = 'DISABLE' if is_enabled else 'ENABLE'

        if self.action == 'DISABLE':
            if is_enabled:
                self.quit(context)
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Virtual Reality Display is not enabled")
                return {'CANCELLED'}

        elif self.action == 'ENABLE':
            if is_enabled:
                self.report({'ERROR'}, "Virtual Reality Display is already enabled")
                return {'CANCELLED'}

            if self.init(context):
                return {'RUNNING_MODAL'}
            else:
                # quit right away
                vr.is_enabled = False
                self._quit(context)

        elif self.action == 'RECENTER':
            vr.command_push(Commands.recenter)
            return {'FINISHED'}

        else:
            assert False, "action \"{0}\" not implemented".format(self.action)

        return {'CANCELLED'}

    def quit(self, context):
        """garbage collect"""
        # change it so the original modal operator will clean things up
        wm = context.window_manager
        wm.virtual_reality.reset()

    def _quit(self, context):
        """actual quit"""

        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None

        self._preview.quit()

        if self._hmd:
            self._hmd.quit()

        # cleanup viewport
        if context.area:
            context.area.tag_redraw()

    def init(self, context):
        """
        Initialize the callbacks and the external devices
        """
        wm = context.window_manager
        vr = wm.virtual_reality

        vr.is_enabled = True
        vr.error_message = ""

        display_backend = getDisplayBackend(context)
        self._hmd = HMD(display_backend, context, self._error_callback)
        self._preview = Preview()

        self._hash_master = hash(context.area)

        # setup modal
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self._draw_callback_px, (context,), 'WINDOW', 'POST_PIXEL')
        wm.modal_handler_add(self)

        if self._hmd.is_direct_mode:
            self._masterInit(context)
        else:
            return self._slaveHook(context)

        return True

    def _init(self, context):
        if not self._hmd.init(context):
            self.report({'ERROR'}, "Error initializing device")
            return False

        # get the data from device
        color_object = [0, 0]
        for i in range(2):
            self._hmd.setEye(i)
            color_object[i] = self._hmd.color_object

        self._preview.init(color_object[0], color_object[1])
        return True

    def _masterInit(self, context):
        return self._init(context)

    def _slaveInit(self, context):
        self._slave_setup = True

        if not self._init(context):
            self.quit(context)

    def _slaveHook(self, context):
        self._hash_slave = -1
        self._slave_setup = False

        hashes = []

        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    hashes.append(hash(area))

        bpy.ops.screen.area_dupli('INVOKE_DEFAULT')

        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type != 'VIEW_3D':
                    continue

                _hash = hash(area)

                try:
                    hashes.remove(_hash)

                except ValueError:
                    self._hash_slave = _hash
                    print('Success finding slave')
                    return True

        return False

    def _commands(self, context):
        """
        Process any pending command from the main window
        """
        wm = context.window_manager
        vr = wm.virtual_reality

        while vr.commands:
            command = vr.command_pop()

            if command == Commands.recenter:
                if self._hmd:
                    self._hmd.reCenter()

            elif command == Commands.test:
                print("Testing !!!")

    def _loop(self, context):
        """
        Get fresh tracking data and render into the FBO
        """
        self._commands(context)
        self._hmd.loop(context)

        for i in range(2):
            self._hmd.setEye(i)

            offscreen_object = self._hmd.offscreen_object
            projection_matrix = self._hmd.projection_matrix
            modelview_matrix = self._hmd.modelview_matrix

            # drawing
            offscreen_object.draw_view3d(projection_matrix, modelview_matrix)

        self._hmd.frameReady()

    def _drawMaster(self, context):
        wm = context.window_manager
        vr = wm.virtual_reality

        if self._hmd.is_direct_mode:
            self._loop(context)

        if vr.use_preview:
            self._preview.loop(vr.preview_scale)

    def _drawSlave(self, context):
        if self._hmd.is_direct_mode:
            return

        if not self._slave_setup:
            self._slaveInit(context)

        self._loop(context)
        area.tag_redraw()

    def _draw_callback_px(self, context):
        """
        callback function, run every time the viewport is refreshed
        """
        area = context.area
        hash_area = hash(area)

        if hash_area == self._hash_slave:
            self._drawSlave(context)

        elif hash_area == self._hash_master:
            self._drawMaster(context)

    def _error_callback(self, message, is_fatal):
        """
        Error handler, called from HMD class
        """
        context = bpy.context
        wm = context.window_manager
        vr = wm.virtual_reality

        if is_fatal:
            self.report({'ERROR'}, message)
            self.quit(context)

        vr.error_message = message


# ############################################################
# Global Properties
# ############################################################

from bpy.props import (
        BoolProperty,
        CollectionProperty,
        EnumProperty,
        StringProperty,
        IntProperty,
        )

class VirtualRealityCommandInfo(bpy.types.PropertyGroup):
    action = EnumProperty(
        name="Action",
        items=(("NONE", "None", ""),
               (Commands.recenter, "Re-Center", ""),
               (Commands.test, "Test", ""),
               ),
        default="NONE",
        )


class VirtualRealityInfo(bpy.types.PropertyGroup):
    is_enabled = BoolProperty(
            name="Enabled",
            default=False,
            )

    use_preview = BoolProperty(
        name="Preview",
        default=False,
        )

    preview_scale = IntProperty(
            name="Preview Scale",
            min=0,
            max=100,
            default=20,
            subtype='PERCENTAGE',
            )

    error_message = StringProperty(
            name="Error Message",
            )

    tracking_mode = EnumProperty(
        name="Tracking Mode",
        description="",
        items=(("ALL", "All", ""),
               ("ROTATION", "Rotation Only", "Ignore positional tracking data"),
               ("NONE", "None", "No tracking"),
               ),
        default="ALL",
        )

    commands = CollectionProperty(type=VirtualRealityCommandInfo)


    def command_push(self, action):
        command = self.commands.add()
        command.action = action

    def command_pop(self):
        command = self.commands[0]
        action = command.action
        self.commands.remove(0)
        return action

    def reset(self):
        while self.commands:
            self.commands.remove(0)

        self.use_preview = False
        self.error_message = ""
        self.is_enabled = False


# ############################################################
# Callbacks
# ############################################################

@persistent
def virtual_reality_load_pre(dummy):
    wm = bpy.context.window_manager
    wm.virtual_reality.reset()


@persistent
def virtual_reality_load_post(dummy):
    wm = bpy.context.window_manager
    wm.virtual_reality.reset()


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.app.handlers.load_pre.append(virtual_reality_load_pre)
    bpy.app.handlers.load_pre.append(virtual_reality_load_post)

    bpy.utils.register_class(VirtualRealityDisplayOperator)
    bpy.utils.register_class(VirtualRealityCommandInfo)
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
    bpy.utils.unregister_class(VirtualRealityCommandInfo)

