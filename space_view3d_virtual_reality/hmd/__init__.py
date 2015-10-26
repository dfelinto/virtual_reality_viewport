
TODO = True

from mathutils import (
        Matrix,
        Quaternion,
        )

import gpu

VERBOSE = True


# ############################################################
# Data structs
# ############################################################

def HMD(display_backend, context, error_callback):
    """
    return the head mounted display device class
    (defined in another file)

    :param display_backend: backend engine
    :type display_backend: str
    :param context: BPY context
    :type context: bpy.types.Context
    :param error_callback: error handler
    :type error_callback: func(message, is_fatal)
    """
    from .oculus import Oculus
    from .oculus_legacy import OculusLegacy
    from .debug import Debug

    displays = {
            'OCULUS':Oculus,
            'OCULUS_LEGACY':OculusLegacy,
            'DEBUG':Debug,
            }

    if display_backend not in displays:
        assert False, "Display Backend \"{0}\" not implemented".format(display_backend)

    return displays[display_backend](context, error_callback)


# ############################################################
# Base class inherited by HMD devices
# ############################################################

class HMD_Base:
    __slots__ = {
        "_name",
        "_current_eye",
        "_error_callback",
        "_width",
        "_height",
        "_projection_matrix",
        "_head_transformation",
        "_is_direct_mode",
        "_eye_pose",
        "_offscreen",
        "_color_texture",
        "_modelview_matrix",
        "_near",
        "_far",
        }

    def __init__(self, name, is_direct_mode, context, error_callback):
        self._name = name
        self._is_direct_mode = is_direct_mode
        self._error_callback = error_callback
        self._current_eye = 0
        self._width = [0, 0]
        self._height = [0, 0]
        self._projection_matrix = [Matrix.Identity(4), Matrix.Identity(4)]
        self._modelview_matrix = [Matrix.Identity(4), Matrix.Identity(4)]
        self._color_texture = [0, 0]
        self._offscreen = [None, None]
        self._eye_orientation_raw = [[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]]
        self._eye_position_raw = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        self._scale = self._calculateScale(context)

        self._updateViewClipping(context)

    @property
    def is_direct_mode(self):
        return self._is_direct_mode

    @property
    def width(self):
        return self._width[self._current_eye]

    @width.setter
    def width(self, value):
        self._width[self._current_eye] = value

    @property
    def height(self):
        return self._height[self._current_eye]

    @height.setter
    def height(self, value):
        self._height[self._current_eye] = value

    @property
    def offscreen(self):
        return self._offscreen[self._current_eye]

    @property
    def color_texture(self):
        return self._color_texture[self._current_eye]

    @property
    def projection_matrix(self):
        return self._projection_matrix[self._current_eye]

    @property
    def modelview_matrix(self):
        return self._modelview_matrix[self._current_eye]

    def setEye(self, eye):
        self._current_eye = int(bool(eye))

    def init(self):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        try:
            for i in range(2):
                self._offscreen[i] = gpu.offscreen.new(self._width[i], self._height[i], 0)
                if hasattr(self._offscreen[i], "color_texture"):
                    self._color_texture[i] = self._offscreen[i].color_texture
                else: # TODO remove this once the patch is merged
                    self._color_texture[i] = self._offscreen[i].color_object

        except Exception as E:
            print(E)
            self._offscreen[0] = None
            self._offscreen[1] = None
            return False

        else:
            return True

    def loop(self, context):
        """
        Get fresh tracking data
        """
        self._updateViewClipping(context)
        self.updateMatrices(context)

    def frameReady(self):
        """
        The frame is ready to be sent to the device
        """
        assert False, "frameReady() not implemented for the \"{0}\" device".format(self._name)

    def reCenter(self):
        """
        Re-center the HMD device

        :return: return True if success
        :rtype: bool
        """
        assert False, "reCenter() not implemented for the \"{0}\" device".format(self._name)

    def quit(self):
        """
        Garbage collection
        """
        try:
            for i in range(2):
                self._offscreen[i] = None

        except Exception as E:
            print(E)

    def error(self, function, exception, is_fatal):
        """
        Handle error messages
        """
        if VERBOSE:
            print("ADD-ON :: {0}() : {1}".format(function, exception))
            import sys
            traceback = sys.exc_info()

            if traceback and traceback[0]:
                print(traceback[0])

        if hasattr(exception, "strerror"):
            message = exception.strerror
        else:
            message = str(exception)

        # send the error the interface
        self._error_callback(message, is_fatal)

    def updateMatrices(self, context):
        """
        Update OpenGL drawing matrices
        """
        vr = context.window_manager.virtual_reality

        tracking_mode = vr.tracking_mode
        view_matrix = self._getViewMatrix(context, vr.lock_camera)

        for i in range(2):
            if tracking_mode == 'NONE':
                self._modelview_matrix[i] = view_matrix
                continue

            rotation_raw = self._eye_orientation_raw[i]
            rotation = Quaternion(rotation_raw).to_matrix().to_4x4()

            if tracking_mode == 'ALL':
                position_raw = self._eye_position_raw[i]

                # take scene units into consideration
                position_raw = self._scaleMovement(position_raw)
                position = Matrix.Translation(position_raw)

                transformation = position * rotation

            else: # 'ROTATION'
                # rotation only, ignore the positional data
                transformation = rotation

            self._modelview_matrix[i] = transformation.inverted() * view_matrix

    def _getViewMatrix(self, context, lock_camera):
        region = context.region_data

        if (self._is_direct_mode and lock_camera) or (region.view_perspective == 'CAMERA'):
            space = context.space_data
            camera = space.camera
            return camera.matrix_world.inverted()
        else:
            return region.view_matrix.copy()

    def _updateViewClipping(self, context):
        space = context.space_data
        region = context.region_data

        if region.view_perspective == 'CAMERA':
            camera_ob = space.camera
            camera = camera_ob.data

            self._near = camera.clip_start
            self._far = camera.clip_end
        else:
            self._near = space.clip_start
            self._far = space.clip_end

    def _calculateScale(self, context):
        """
        if BU != 1 meter, scale the transformations
        """
        scene = context.scene

        unit_settings = scene.unit_settings
        system = unit_settings.system

        if system == 'NONE':
            return None

        elif system == 'METRIC':
            return 1.0 / unit_settings.scale_length

        elif system == 'IMPERIAL':
            return 0.3048 / unit_settings.scale_length

        else:
            assert('Unit system not supported ({0})'.format(system))

    def _scaleMovement(self, position):
        """
        if BU != 1 meter, scale the transformations
        """
        if self._scale is None:
            return position

        return [position[0] * self._scale,
                position[1] * self._scale,
                position[2] * self._scale]

    def _convertMatrixTo4x4(self, value):
        matrix = Matrix()

        matrix[0] = value[0:4]
        matrix[1] = value[4:8]
        matrix[2] = value[8:12]
        matrix[3] = value[12:16]

        return matrix.transposed()

