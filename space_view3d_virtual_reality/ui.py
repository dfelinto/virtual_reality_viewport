import bpy


# ############################################################
# User Interface
# ############################################################

class VirtualRealityPanel(bpy.types.Panel):
    bl_label = "Head Mounted Display"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Virtual Reality'

    @staticmethod
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        vr = wm.virtual_reality

        col = layout.column()

        if not vr.is_enabled:
            col.operator("view3d.virtual_reality_display", text="Virtual Reality").action='ENABLE'
        else:
            col.operator("view3d.virtual_reality_display", text="Virtual Reality", icon="X").action='DISABLE'

            box = col.box()
            col = box.column()

            if vr.is_slave_setup:
                col.operator("view3d.virtual_reality_display", text="Start", icon="CAMERA_STEREO").action='FULLSCREEN'

            else:
                if vr.is_paused:
                    col.operator("view3d.virtual_reality_display", text="Play", icon="PLAY").action='PLAY'
                else:
                    col.operator("view3d.virtual_reality_display", text="Pause", icon="PAUSE").action='PAUSE'

                    col.row().prop(vr, "viewport_shade", expand=True)

                    row = col.row()
                    row.prop(vr, "use_preview")
                    sub = row.column()
                    sub.active = vr.use_preview
                    sub.prop(vr, "preview_scale", text="Scale")

                    sub = col.column()
                    sub.active = not (vr.use_preview and vr.preview_scale == 100)
                    sub.prop(vr, "use_hmd_only")

                    col.operator("view3d.virtual_reality_display", text="Re-Center").action='RECENTER'

                    col.label(text="Tracking:")
                    row = col.row()
                    row.active = vr.viewport_shade != 'RENDERED'
                    row.prop(vr, "tracking_mode", expand=True)

                    col.prop(vr, "lock_camera")

                    if vr.error_message:
                        col.separator()
                        col.label(text=vr.error_message)

                    #col.separator()
                    #col.prop(vr, "is_debug")


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.utils.register_class(VirtualRealityPanel)


def unregister():
    bpy.utils.unregister_class(VirtualRealityPanel)

