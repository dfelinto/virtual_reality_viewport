import bpy

from bpy.app.handlers import persistent

from .hmd import HMD

from .preview import Preview

from .lib import (
        getDisplayBackend,
        isMac,
        )


TODO = False


# ############################################################
# Commands
# ############################################################

class Commands:
    recenter = 'RECENTER'
    fullscreen = 'FULLSCREEN'
    play = 'PLAY'
    pause = 'PAUSE'
    test = 'TEST'


class SlaveStatus:
    non_setup    = 0   # initial
    dupli        = 1   # view3d duplicated
    uiless       = 2   # view3d without UI
    waituser     = 3   # waiting for user to move window to HMD
    usermoved    = 4   # user moved window
    ready        = 5   # all went well
    play         = 6   # play
    pause        = 7   # pause
    paused       = 8   # paused
    error        = 9   # something didn't work


# ############################################################
# Main Operator
# ############################################################

class VirtualRealityDisplayOperator(bpy.types.Operator):
    """"""
    bl_idname = "view3d.virtual_reality_display"
    bl_label = "Toggle Virtual Reality Display"
    bl_description = ""

    # update the values in def _init_static
    _hmd = None
    _timer = None
    _handle_pre = None
    _handle_post = None
    _handle_pixel = None
    _hash_slave = -1
    _hash_master = -1
    _slave_status = 0
    _slave_window = None
    _slave_area = None
    _is_mac = False
    _visible_master = None
    _visible_slave = None
    _is_rendering = False

    action = bpy.props.EnumProperty(
        description="",
        items=(("ENABLE", "Enable", "Enable"),
               ("DISABLE", "Disable", "Disable"),
               ("TOGGLE", "Toggle", "Toggle"),
               ("RECENTER", "Re-Center", "Re-Center tracking data"),
               ("FULLSCREEN", "Fullscreen", "Make slave fullscreen"),
               ("PLAY", "Play", ""),
               ("PAUSE", "Pause", ""),
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

        if event.type == 'TIMER' and \
           not vr.is_paused:
            if self._slave_area:
                self._slave_area.tag_redraw()

            if vr.use_preview:
                area.tag_redraw()

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

        elif self.action == 'FULLSCREEN':
            vr.command_push(Commands.fullscreen)
            return {'FINISHED'}

        elif self.action == 'PLAY':
            vr.command_push(Commands.play)
            # we define is_paused right away, so
            # the next MODAL loop already tag_redraw
            vr.is_paused = False
            return {'FINISHED'}

        elif self.action == 'PAUSE':
            vr.command_push(Commands.pause)
            self._redraw(context)
            return {'FINISHED'}

        else:
            assert False, "action \"{0}\" not implemented".format(self.action)

        return {'CANCELLED'}

    def _redraw(self, context, redraw_master=True, redraw_slave=True):
        if redraw_slave and self._slave_area:
            self._slave_area.tag_redraw()

        if redraw_master:
            context.area.tag_redraw()

    def quit(self, context):
        """garbage collect"""
        # change it so the original modal operator will clean things up
        wm = context.window_manager
        wm.virtual_reality.reset()

    def _quit(self, context):
        """actual quit"""

        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)
            self._timer = None

        if self._handle_pre:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_pre, 'WINDOW')
            self._handle_pre = None

        if self._handle_post:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_post, 'WINDOW')
            self._handle_post = None

        if self._handle_pixel:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_pixel, 'WINDOW')
            self._handle_pixel = None

        self._preview.quit()

        if self._hmd:
            self._hmd.quit()

        if self._slave_window:
            if hasattr(self._slave_window, "close"):
                self._slave_window.close()
            else:
                print("Error closing HMD window")

        # cleanup viewport
        if context.area:
            context.area.tag_redraw()

    def _init_static(self):
        self._hmd = None
        self._timer = None
        self._handle_pre = None
        self._handle_post = None
        self._handle_pixel = None
        self._hash_slave = -1
        self._hash_master = -1
        self._slave_status = 0
        self._slave_window = None
        self._slave_area = None
        self._is_mac = isMac()
        self._visible_master = None
        self._visible_slave = None
        self._is_rendering = False

    def init(self, context):
        """
        Initialize the callbacks and the external devices
        """
        wm = context.window_manager
        vr = wm.virtual_reality

        vr.reset()
        vr.is_enabled = True

        self._init_static()

        display_backend = getDisplayBackend(context)
        self._hmd = HMD(display_backend, context, self._error_callback)
        self._preview = Preview()

        self._hash_master = hash(context.area)

        # setup modal
        self._timer = wm.event_timer_add(1.0 / 75.0, context.window) # 75 Hz
        self._handle_pre = bpy.types.SpaceView3D.draw_handler_add(self._draw_callback_pre, (context,), 'WINDOW', 'PRE_VIEW')
        self._handle_post = bpy.types.SpaceView3D.draw_handler_add(self._draw_callback_post, (context,), 'WINDOW', 'POST_VIEW')
        self._handle_pixel = bpy.types.SpaceView3D.draw_handler_add(self._draw_callback_pixel, (context,), 'WINDOW', 'POST_PIXEL')
        wm.modal_handler_add(self)

        if self._hmd.is_direct_mode:
            self._init(context)
        else:
            vr.is_slave_setup = True
            return self._slaveSetup(context)

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

    def _slaveSetup(self, context):
        ok = True

        if self._slave_status == SlaveStatus.error:
            return False

        elif self._slave_status == SlaveStatus.non_setup:
            ok = self._slaveHook(context, SlaveStatus.dupli)
            self._slave_status = SlaveStatus.dupli

        elif self._slave_status == SlaveStatus.dupli:
            ok = self._slaveHook(context, SlaveStatus.uiless)
            self._slave_status = SlaveStatus.waituser

        elif self._slave_status == SlaveStatus.waituser:
            # waiting for the user input
            return True

        elif self._slave_status == SlaveStatus.usermoved:
            if not self._is_mac:
                bpy.ops.wm.window_fullscreen_toggle()

            space = context.space_data
            if space.camera:
                region = context.region_data
                region.view_perspective = 'CAMERA'

            context.window_manager.virtual_reality.is_slave_setup = False
            ok = self._init(context)
            self._slave_status = SlaveStatus.ready

        elif self._slave_status == SlaveStatus.play:
            context.window_manager.virtual_reality.is_paused = False
            self._slave_status = SlaveStatus.ready

        elif self._slave_status == SlaveStatus.pause:
            context.window_manager.virtual_reality.is_paused = True
            context.area.tag_redraw()
            self._slave_status = SlaveStatus.paused

        else:
            assert False, "_slaveSetup: Slave status \"{0}\" not defined".format(self._slave_status)

        if not ok:
            self._slave_status = SlaveStatus.error
            self.quit(context)

        self._slave_window = context.window
        return ok

    def _slaveHook(self, context, mode=''):
        self._hash_slave = -1
        self._slave_area = None
        self._slave_status = SlaveStatus.non_setup

        hashes = []

        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    hashes.append(hash(area))

        if mode == SlaveStatus.dupli:
            bpy.ops.screen.area_dupli('INVOKE_DEFAULT')

        elif mode == SlaveStatus.uiless:
            bpy.ops.screen.screen_full_area(use_hide_panels=True)

        else:
            assert False, "_slaveHook: Slave status \"{0}\" not defined".format(self._slave_status)

        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type != 'VIEW_3D':
                    continue

                _hash = hash(area)

                try:
                    hashes.remove(_hash)

                except ValueError:
                    self._hash_slave = _hash
                    self._slave_area = area
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

            elif command == Commands.fullscreen:
                self._slave_status = SlaveStatus.usermoved
                self._slaveSetup(context)

            elif command == Commands.play:
                self._slave_status = SlaveStatus.play
                self._slaveSetup(context)

            elif command == Commands.pause:
                self._slave_status = SlaveStatus.pause
                self._slaveSetup(context)

            elif command == Commands.test:
                print("Testing !!!")

            else:
                assert False, "_commands: command \"{0}\" not implemented"

    def _loop(self, context):
        """
        Get fresh tracking data and render into the FBO
        """
        self._is_rendering = True
        self._hmd.loop(context)

        for i in range(2):
            self._hmd.setEye(i)

            offscreen_object = self._hmd.offscreen_object
            projection_matrix = self._hmd.projection_matrix
            modelview_matrix = self._hmd.modelview_matrix

            # drawing
            offscreen_object.draw_view3d(projection_matrix, modelview_matrix)

        self._hmd.frameReady()
        self._is_rendering = False

    def _drawMaster(self, context):
        wm = context.window_manager
        vr = wm.virtual_reality

        if self._hmd.is_direct_mode:
            self._commands(context)

        if vr.is_paused:
            return

        if self._hmd.is_direct_mode:
            self._loop(context)

        if vr.use_preview:
            self._preview.loop(vr.preview_scale)

    def _drawSlave(self, context):
        wm = context.window_manager
        vr = wm.virtual_reality

        if self._hmd.is_direct_mode:
            return

        self._commands(context)

        if vr.is_paused:
            return

        if self._slave_status == SlaveStatus.ready:
            self._loop(context)

        elif self._slave_status == SlaveStatus.paused:
            return

        elif self._slave_status == SlaveStatus.waituser:
            self._drawDisplayMessage(context)

        else:
            self._slaveSetup(context)

    def _drawDisplayMessage(self, context):
        """
        Message telling user to move the window the HMD display
        """
        from bgl import glColor4f

        window = context.window
        width = window.width
        height = window.height

        glColor4f(1.0, 1.0, 1.0, 1.0)
        font_id = 0

        # draw some text
        x = int(0.1 * width)
        y = int(0.5 * height)
        font_size = int(width * 0.035)
        line_gap = int(font_size * 1.5)

        from blf import (
                SHADOW,
                enable,
                shadow,
                shadow_offset,
                position,
                size,
                draw,
                disable,
                )

        enable(font_id, SHADOW)
        shadow(font_id, 5, 0.0, 0.0, 0.0, 1.0)
        shadow_offset(font_id, -2, -2)
        size(font_id, font_size, 72)

        if self._is_mac:
            position(font_id, x, y + line_gap, 0)
            draw(font_id, "1. Move this window to the external HMD display")
            position(font_id, x, y, 0)
            draw(font_id, "2. Set this window to fullscreen (Alt + F11)")
            position(font_id, x, y - line_gap, 0)
            draw(font_id, "3. Select \"Start\" in the main window")
        else:
            position(font_id, x, y, 0)
            draw(font_id, "1. Move this window to the external HMD display")
            position(font_id, x, y - line_gap, 0)
            draw(font_id, "2. Select \"Start\" in the main window")

        disable(font_id, SHADOW)

    def _pre_draw_hide(self, context, visible):
        scene = context.scene
        for ob in scene.objects:
            if not ob.hide:
                visible.append(ob)
                ob.hide = True

    def _post_draw_show(self, context, visible):
        for ob in visible:
            ob.hide = False

    def _hide_master(self, context):
        """
        whether to hide the main 3d viewport
        """
        vr = context.window_manager.virtual_reality
        if vr.use_hmd_only:
            return True

        if vr.use_preview and vr.preview_scale == 100:
            return True

    def _draw_callback_pre(self, context):
        """
        hide all the scene objects to speed up rendering
        """
        if self._is_rendering or \
           context.window_manager.virtual_reality.is_debug:
            return

        area = context.area
        hash_area = hash(area)

        if hash_area == self._hash_slave:
            self._visible_slave = []
            self._pre_draw_hide(context, self._visible_slave)

        elif hash_area == self._hash_master and self._hide_master(context):
            self._visible_master = []
            self._pre_draw_hide(context, self._visible_master)

    def _draw_callback_post(self, context):
        """
        show all the hidden objects
        """
        if self._is_rendering or \
           context.window_manager.virtual_reality.is_debug:
            return

        area = context.area
        hash_area = hash(area)

        if hash_area == self._hash_slave:
            self._post_draw_show(context, self._visible_slave)

        elif hash_area == self._hash_master and self._hide_master(context):
            self._post_draw_show(context, self._visible_master)

    def _draw_callback_pixel(self, context):
        """
        callback function, run every time the viewport is refreshed
        """
        if self._is_rendering:
            return

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
               (Commands.fullscreen, "Fullscreen", ""),
               (Commands.play, "Play", ""),
               (Commands.pause, "Pause", ""),
               (Commands.test, "Test", ""),
               ),
        default="NONE",
        )


class VirtualRealityInfo(bpy.types.PropertyGroup):
    is_enabled = BoolProperty(
            name="Enabled",
            default=False,
            )

    is_paused = BoolProperty(
            name="Paused",
            default=False,
            )

    use_preview = BoolProperty(
        name="Preview",
        default=False,
        )

    use_hmd_only = BoolProperty(
        name="HMD Only",
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

    is_slave_setup = BoolProperty(
        default = False,
        )

    is_debug = BoolProperty(
        name = "Debug",
        default = False,
        description = "Skip the optimization to prevent extra drawing",
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
        self.use_hmd_only = False
        self.error_message = ""
        self.is_enabled = False
        self.is_slave_setup = False
        self.is_paused = False
        self.is_debug = False


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

