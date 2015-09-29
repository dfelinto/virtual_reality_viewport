
TODO = True

from mathutils import (
        Matrix,
        Vector,
        )

import gpu


# ############################################################
# Data structs
# ############################################################

def HMD(display_backend):
    """
    return the head mounted display device class
    (defined in another file)

    :param display_backend: asdasd
    :type display_backend: str
    """
    from .oculus import Oculus
    from .debug import Debug

    displays = {
            'OCULUS':Oculus,
            'DEBUG':Debug,
            }

    if display_backend not in displays:
        assert False, "Display Backend \"{0}\" not implemented".format(display_backend)

    return displays[display_backend]()


# ############################################################
# Data structs
# ############################################################

class HMD_Data:
    status = None
    projection_matrix = Matrix.Identity(4)
    modelview_matrix = Matrix.Identity(4)
    interpupillary_distance = Vector((0.0, 0.0))
    width = 0
    height = 0
    framebuffer_object = 0
    color_object = 0


# ############################################################
# Base class inherited by HMD devices
# ############################################################

class HMD_Base:
    __slots__ = {
        "_color_object",
        "_current_eye",
        "_framebuffer_object",
        "_height",
        "_interpupillary_distance",
        "_modelview_matrix",
        "_name",
        "_offscreen_object",
        "_projection_matrix",
        "_width",
        }

    def __init__(self, name):
        self._name = name
        self._current_eye = 0
        self._width = 0
        self._height = 0
        self._projection_matrix = [Matrix.Identity(4), Matrix.Identity(4)]
        self._modelview_matrix = [Matrix.Identity(4), Matrix.Identity(4)]
        self._interpupillary_distance = Vector((0.0, 0.0))
        self._framebuffer_object = [0, 0]
        self._color_object = [0, 0]
        self._offscreen_object = [None, None]

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def offscreen_object(self):
        return self._offscreen_object[self._current_eye]

    @property
    def framebuffer_object(self):
        return self._framebuffer_object[self._current_eye]

    @property
    def color_object(self):
        return self._color_object[self._current_eye]

    @property
    def projection_matrix(self):
        return self._projection_matrix[self._current_eye]

    @property
    def modelview_matrix(self):
        return self._modelview_matrix[self._current_eye]

    def setEye(self, eye):
        self._current_eye = int(bool(eye))

    def isConnected(self):
        """
        Check if device is connected

        :return: return True if the device is connected
        :rtype: bool
        """
        assert False, "isConnected() not implemented for the \"{0}\" device".format(self._name)

    def init(self):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        try:
            for i in range(2):
                self._offscreen_object[i] = gpu.offscreen_object_create(self._width, self._height)
                self._framebuffer_object[i] = self._offscreen_object[i].framebuffer_object
                self._color_object[i] = self._offscreen_object[i].color_object

        except Exception as E:
            print(E)
            return False

        else:
            return True

    def loop(self, context):
        """
        Get fresh tracking data
        """
        self.updateMatrices(context)

    def frameReady(self):
        """
        The frame is ready to be sent to the device
        """
        assert False, "frameReady() not implemented for the \"{0}\" device".format(self._name)

    def quit(self):
        """
        Garbage collection
        """
        try:
            for i in range(2):
                gpu.offscreen_object_free(self._offscreen_object[i])

        except Exception as E:
            print(E)

    def updateMatrices(self, context):
        """
        Update OpenGL drawing matrices
        """
        TODO


