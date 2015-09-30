
TODO = True

from mathutils import (
        Matrix,
        Vector,
        )

import gpu

VERBOSE = True


# ############################################################
# Data structs
# ############################################################

def HMD(display_backend, error_callback):
    """
    return the head mounted display device class
    (defined in another file)

    :param display_backend: backend engine
    :type display_backend: str
    :param error_callback: error handler
    :type error_callback: func(message, is_fatal)
    """
    from .oculus import Oculus
    from .debug import Debug

    displays = {
            'OCULUS':Oculus,
            'DEBUG':Debug,
            }

    if display_backend not in displays:
        assert False, "Display Backend \"{0}\" not implemented".format(display_backend)

    return displays[display_backend](error_callback)


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
        "_eye_pose",
        "_offscreen_object",
        "_framebuffer_object",
        "_color_object",
        "_modelview_matrix",
        }

    def __init__(self, name, error_callback):
        self._name = name
        self._error_callback = error_callback
        self._current_eye = 0
        self._width = 0
        self._height = 0
        self._projection_matrix = [Matrix.Identity(4), Matrix.Identity(4)]
        self._modelview_matrix = [Matrix.Identity(4), Matrix.Identity(4)]
        self._framebuffer_object = [0, 0]
        self._color_object = [0, 0]
        self._offscreen_object = [None, None]
        self._eye_pose = [Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 0.0))]
        self._head_transformation = [Matrix.Identity(4), Matrix.Identity(4)]

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
        TODO

