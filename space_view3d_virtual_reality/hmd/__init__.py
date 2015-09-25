
TODO = True

from mathutils import (
        Matrix,
        Vector,
        )


class HMD_Data:
    status = None
    projection_matrix = Matrix()
    modelview_matrix = Matrix()
    interpupillary_distance = Vector((0.0, 0.0))
    width = 0
    height = 0
    fbo = 0
    texture = 0


class HMD:
    __slots__ = {
        "_device",
        "_projection_matrix",
        "_modelview_matrix",
        "_interpupillary_distance",
        "_width",
        "_height",
        "_fbo",
        "_texture",
        }

    def __init__(self, display_backend):
        self._device = None
        self._projection_matrix = Matrix()
        self._modelview_matrix = Matrix()
        self._interpupillary_distance = Vector((0.0, 0.0))
        self._width = 0
        self._height = 0
        self._fbo = 0
        self._texture = 0

        from .oculus import Oculus
        from .debug import Debug

        displays = {
                'OCULUS':Oculus,
                'DEBUG':Debug,
                }

        assert(display_backend in displays)
        self._device = displays[display_backend]()

    @property
    def fbo(self):
        return self._fbo

    @property
    def texture(self):
        return self._texture

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def projection_matrix(self):
        return self._projection_matrix

    @property
    def modelview_matrix(self):
        return TODO

    def isConnected(self):
        """
        Check if device is connected

        :return: return True if the device is connected
        :rtype: bool
        """
        return self._device.isConnected()

    def init(self):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        return self._device.init()

    def loop(self):
        """
        Get fresh tracking data
        """
        return self._device.loop()

    def frameReady(self):
        """
        The frame is ready to be send to the device
        """
        return self._device.frameReady()

    def quit(self):
        """
        Garbage collection
        """
        return self._device.quit()

