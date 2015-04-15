#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

# <pep8 compliant>
bl_info = {
    "name": "Virtual Reality Viewport",
    "author": "Dalai Felinto",
    "version": (0, 9),
    "blender": (2, 7, 5),
    "location": "Window Menu",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"}


import bpy

from bgl import (
        Buffer,
        GL_INT,
        GL_RGBA,
        )

from .opengl_helper import (
        calculate_image_size,
        create_image,
        create_shader,
        delete_image,
        draw_callback_px,
        resize,
        )

from . import oculus

def get_context_3dview (context):
    """returns area and space"""
    screen = context.screen

    for area in screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    return area, region

    return None, None


def get_space_3dview(context):
    area = context.area
    for space in area.spaces:
        if space.type == 'VIEW_3D':
            return space
    return None


def get_glsl_shader():
    import os
    folderpath = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(folderpath, 'oculus_dk2.glsl')
    f = open(filepath, 'r')
    data = f.read()
    f.close()
    return data


class VirtualRealityViewportOperator(bpy.types.Operator):
    """"""
    bl_idname = "view3d.virtual_reality_toggle"
    bl_label = "Toggle Virtual Reality Mode"
    bl_description = ""

    _enabled = True
    _timer = None
    _display_mode = None
    _is_multiview = None
    _space = None

    @classmethod
    def poll(cls, context):
        camera = context.scene.camera
        return camera and camera.type == 'CAMERA'

    def modal(self, context, event):
        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':

            # bug, waiting for fix: "[#31026] context.region broken after QuadView on + off"
            # http://projects.blender.org/tracker/index.php?func=detail&aid=31026&group_id=9&atid=498
            if not context.region or \
                not context.space_data or \
                context.space_data.type != 'VIEW_3D':
                return {'PASS_THROUGH'}

            viewport_shade = context.space_data.viewport_shade
            self._enabled = (viewport_shade != 'RENDERED')

            if (self.width != context.region.width) or (self.height != context.region.height):
                resize(self, context)

            self.oculus.update()


        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        """
        * Create a fullscreen window with the editor in fullscreen with clean UI.
        * Views should be on, and this window should have stereo 3d mode set to side-by-side
        * Also you should lock a camera to the viewport to make sure you always look nicely
        * Sync the Oculus rotation + translation to the Blender camera
        * Now the opengl fun ... create a GLSL screen shader to run the warping distortions.
        """

        if context.area.type == 'VIEW_3D':
            scene = context.scene
            window = context.window

            self.oculus = oculus.Oculus(scene.camera, self.report)

            if not self.oculus.isAvailable():
                return {'CANCELLED'}

            self._is_multiview = scene.render.use_multiview
            self._display_mode = window.stereo_3d_display.display_mode

            #if bpy.ops.wm.window_fullscreen_toggle.poll():
            #    bpy.ops.wm.window_fullscreen_toggle()

            scene.render.use_multiview = True
            window.stereo_3d_display.display_mode = 'SIDEBYSIDE'

            #if bpy.ops.screen.screen_full_area.poll():
            #    bpy.ops.screen.screen_full_area(use_hide_panels=True)

            space = get_space_3dview(context)
            self._space = space, space.show_only_render, space.stereo_3d_camera, space.region_3d.view_perspective

            space.show_only_render = True
            space.stereo_3d_camera = 'S3D'
            space.region_3d.view_perspective = 'CAMERA'

            if bpy.ops.view3d.view_all.poll():
                bpy.ops.view3d.view_all()

            self._timer = context.window_manager.event_timer_add(1.0/75.0, context.window) # 75 Hz
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_VIEW')
            context.window_manager.modal_handler_add(self)

            self.viewport = Buffer(GL_INT, 4)
            self.width = context.region.width
            self.height = context.region.height

            # power of two dimensions
            self.buffer_width, self.buffer_height = calculate_image_size(self.width, self.height)

            # images to dump the screen buffers
            self.color_id = create_image(self.buffer_width, self.buffer_height, GL_RGBA)

            # glsl shaders
            fragment_shader = get_glsl_shader()
            self.program_shader = create_shader(fragment_shader)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

    def cancel(self, context):
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            del self._handle

        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            del self._timer

        self.oculus.quit()
        self.quit()

        # set back the original values
        try:
            context.scene.render.use_multiview = self._is_multiview
            context.window.stereo_3d_display.display_mode = self._display_mode
            space, show_only_render, stereo_3d_camera, view_perspective  = self._space
            space.show_only_render = show_only_render
            space.stereo_3d_camera = stereo_3d_camera
            space.region_3d.view_perspective = view_perspective
        except Exception as err:
            self.report({'ERROR'}, err.message)


        return {'CANCELLED'}

    def quit(self):
        """garbage colect"""
        if self.color_id:
            delete_image(self.color_id)

    def is_stereo_left(self, context):
        """"""
        space = get_space_3dview(context)
        return space.stereo_3d_eye == 'LEFT'


def register():
    bpy.utils.register_class(VirtualRealityViewportOperator)


def unregister():
    bpy.utils.unregister_class(VirtualRealityViewportOperator)


if __name__ == '__main__':
    register()
