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
    def __init__(self, error_callback):
        super(Oculus, self).__init__('Oculus', error_callback)
        checkModule('oculus_sdk_bridge')

        # self._debug()

    def _debug(self):
        import bridge
        import bridge_wrapper

        input = 3
        device = bridge_wrapper.Debug_new(input)
        factor = bridge_wrapper.Debug_multiplicationFactor()
        print("Multiplication factor is {0}".format(factor))

        output = bridge_wrapper.Debug_multiplicationResult(device)
        print("Return of {0} is {1}".format(input, output))

    def init(self, context):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        try:
            from bridge.oculus import HMD
            self._hmd = HMD()

            # gather arguments from HMD

            near, far = self._getCameraClipping(context)

            self.setEye(0)
            self.width = self._hmd.width_left
            self.height = self._hmd.height_left
            self.projection_matrix = self._hmd.getProjectionMatrixLeft(near, far)

            self.setEye(1)
            self.width = self._hmd.width_right
            self.height = self._hmd.height_right
            self.projection_matrix = self._hmd.getProjectionMatrixRight(near, far)

            # initialize FBO
            super(Oculus, self).init()

            # send it back to HMD
            if not self._hmd.setup(self._framebuffer_object[0], self._framebuffer_object[1]):
                raise Exception("Failed to setup HMD")

        except Exception as E:
            self.error("init", E, True)
            self._hmd = None
            return False

        else:
            return True

    def loop(self, context):
        """
        Get fresh tracking data
        """
        try:
            data = self._hmd.update()

            self._head_transformation = Matrix(data[0])
            self._eye_pose[0] = Vector(data[1])
            self._eye_pose[1] = Vector(data[2])

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

    def quit(self):
        """
        Garbage collection
        """
        self._hmd = None
        return super(Oculus, self).quit()

