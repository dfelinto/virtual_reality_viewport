"""
Debug
=====

Debug device for testing
"""

from . import baseHMD

VERBOSE = False

def print_debug(*args):
    if VERBOSE:
        print("Debug: {0}".format(*args))


class HMD(baseHMD):
    def __init__(self, context, error_callback):
        super(HMD, self).__init__('HMD', False, context, error_callback)

    def init(self, context):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        print_debug('init()')

        self._width = [512, 512]
        self._height = [512, 512]

        return super(HMD, self).init()

    def loop(self, context):
        """
        Get fresh tracking data
        """
        print_debug('loop()')

        from math import fmod, radians
        from mathutils import Matrix

        global time

        speed = 0.001
        _range = 45.0

        time = fmod(time + speed, 1.0)
        factor = time * 2.0

        if factor > 1.0:
            factor = 2.0 - factor

        one = 1.0 - factor

        # one goes from 0.0 to 1.0, and then from 1.0 to 0.0
        # angle goes from - range * 0.5 to + range * 0.5
        angle = (one * _range) - (_range * 0.5)

        quaternion = list(Matrix.Rotation(radians(angle), 4, 'Y').to_quaternion())

        projection_matrix = self._getProjectionMatrix(context)

        for eye in range(2):
            self._eye_orientation_raw[eye] = quaternion
            self._projection_matrix[eye] = projection_matrix

        super(HMD, self).loop(context)

    def _getProjectionMatrix(self, context):
        region = context.region_data

        if region.view_perspective == 'CAMERA':
            space = context.space_data
            camera = space.camera
            return camera.calc_matrix_camera()
        else:
            return region.perspective_matrix.copy()

    def frameReady(self):
        """
        The frame is ready to be send to the device
        """
        print_debug('frameReady()')

    def quit(self):
        """
        Garbage collection
        """
        print_debug('quit()')
        return super(HMD, self).quit()

global time
time = 0.0

