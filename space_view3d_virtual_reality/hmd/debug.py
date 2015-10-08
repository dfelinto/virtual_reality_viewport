"""
Debug
=====

Debug device for testing
"""

from . import HMD_Base

VERBOSE = False

def print_debug(*args):
    if VERBOSE:
        print("Debug: {0}".format(*args))


class Debug(HMD_Base):
    def __init__(self, context, error_callback):
        super(Debug, self).__init__('Debug', context, error_callback)

    def init(self, context):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        print_debug('init()')

        self._width = [512, 512]
        self._height = [512, 512]

        return super(Debug, self).init()

    def loop(self, context):
        """
        Get fresh tracking data
        """
        print_debug('loop()')
        super(Debug, self).loop(context)

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
        return super(Debug, self).quit()

    def updateMatrices(self, context):
        """
        Update OpenGL drawing matrices
        """
        camera = context.scene.camera

        modelview_matrix = camera.matrix_world.inverted()
        projection_matrix = camera.calc_matrix_camera()

        for i in range(2):
            self._modelview_matrix[i] = modelview_matrix
            self._projection_matrix[i] = projection_matrix


