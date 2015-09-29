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
            col.operator("view3d.virtual_reality_display", text="Virtual Reality", icon="PLAY").action='ENABLE'
        else:
            col.operator("view3d.virtual_reality_display", text="Virtual Reality", icon="X").action='DISABLE'

            col.separator()
            col.prop(vr, "preview_scale", text="Preview")
            row = col.row(align=True)
            row.prop(vr, "color_object_left")
            row.prop(vr, "color_object_right")


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.utils.register_class(VirtualRealityPanel)


def unregister():
    bpy.utils.unregister_class(VirtualRealityPanel)

