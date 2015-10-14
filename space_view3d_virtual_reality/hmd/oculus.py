"""
Oculus
======

Oculus (oculus.com) head mounted display
It uses a C app to connect with the SDK

The bridge code is hosted at Visgraf:
http://git.impa.br/dfelinto/oculus_sdk_bridge
"""

from . import HMD_Base

from ..lib import (
        checkModule,
        )

class Oculus(HMD_Base):
    def __init__(self, context, error_callback):
        super(Oculus, self).__init__('Oculus', True, context, error_callback)
        checkModule('oculus_sdk_bridge')

    def _getHMDClass(self):
        from bridge.oculus import HMD
        return HMD

    @property
    def projection_matrix(self):
        if self._current_eye:
            matrix = self._hmd.getProjectionMatrixRight(self._near, self._far)
        else:
            matrix = self._hmd.getProjectionMatrixLeft(self._near, self._far)

        self.projection_matrix = matrix
        return super(Oculus, self).projection_matrix

    @projection_matrix.setter
    def projection_matrix(self, value):
        self._projection_matrix[self._current_eye] = \
                self._convertMatrixTo4x4(value)

    def init(self, context):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        try:
            HMD = self._getHMDClass()
            self._hmd = HMD()

            # gather arguments from HMD

            self.setEye(0)
            self.width = self._hmd.width_left
            self.height = self._hmd.height_left

            self.setEye(1)
            self.width = self._hmd.width_right
            self.height = self._hmd.height_right

            # initialize FBO
            super(Oculus, self).init()

            # send it back to HMD
            if not self._setup():
                raise Exception("Failed to setup HMD")

        except Exception as E:
            self.error("init", E, True)
            self._hmd = None
            return False

        else:
            return True

    def _setup(self):
        return self._hmd.setup(self._framebuffer_object[0], self._framebuffer_object[1])

    def loop(self, context):
        """
        Get fresh tracking data
        """
        try:
            data = self._hmd.update()

            self._eye_orientation_raw[0] = data[0]
            self._eye_orientation_raw[1] = data[2]
            self._eye_position_raw[0] = data[1]
            self._eye_position_raw[1] = data[3]

            # update matrices
            super(Oculus, self).loop(context)

        except Exception as E:
            self.error("loop", E, False)
            return False

        return True

    def frameReady(self):
        """
        The frame is ready to be sent to the device
        """
        try:
            self._hmd.frameReady()

        except Exception as E:
            self.error("frameReady", E, False)
            return False

        return True

    def reCenter(self):
        """
        Re-center the HMD device

        :return: return True if success
        :rtype: bool
        """
        return self._hmd.reCenter()

    def quit(self):
        """
        Garbage collection
        """
        self._hmd = None
        return super(Oculus, self).quit()

