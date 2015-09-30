"""
Oculus
======

Oculus (oculus.com) head mounted display
It uses a C app to connect with the SDK

The bridge code is hosted at Visgraf:
http://git.impa.br/dfelinto/oculus_sdk_bridge
"""

from mathutils import (
        Vector,
        Matrix,
        )

from . import HMD_Base

from ..lib import (
        checkModule,
        )

class Oculus(HMD_Base):
    def __init__(self):
        super(Oculus, self).__init__('Oculus')
        checkModule('oculus_sdk_bridge')

    def isConnected(self):
        """
        Check if device is connected

        :return: return True if the device is connected
        :rtype: bool
        """
        from bridge.oculus import HMD

        try:
            return HMD.isConnected()

        except Exception as E:
            print(E)
            return False

    def init(self):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        try:
            from bridge.oculus import HMD
            self._hmd = HMD()

            # gather arguments from HMD
            self._width = self._hmd.width
            self._height = self._hmd.height
            self._projection_matrix[0] = self._hmd.projection_matrix_left
            self._projection_matrix[1] = self._hmd.projection_matrix_right

            # initialize FBO
            super(Oculus, self).init()

            # send it back to HMD
            if not self._hmd.setup(self._framebuffer_object[0], self._framebuffer_object[1]):
                raise Exception("Failed to setup HMD")

        except Exception as E:
            print(E)
            self._hmd = None
            return False

        else:
            return True

    def loop(self, context):
        """
        Get fresh tracking data
        """

        data = self._hmd.update()

        self._head_transformation = Matrix(data[0])
        self._eye_pose[0] = Vector(data[1])
        self._eye_pose[1] = Vector(data[2])

        # update matrices
        super(Oculus, self).loop(context)

    def frameReady(self):
        """
        The frame is ready to be sent to the device
        """
        try:
            self._hmd.frameReady()
        except Exception as E:
            return False

    def quit(self):
        """
        Garbage collection
        """
        del self._hmd
        self._hmd = None

        return super(Oculus, self).quit()

