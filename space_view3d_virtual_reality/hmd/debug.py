"""
Debug
=====

Debug device for testing
"""

from . import HMD_Base, HMD_Data

VERBOSE = False

def print_debug(*args):
    if VERBOSE:
        print("Debug: {0}".format(*args))


class Debug(HMD_Base):
    def __init__(self):
        super(Debug, self).__init__('Debug')

    def isConnected(self):
        """
        Check if device is connected

        :return: return True if the device is connected
        :rtype: bool
        """
        print_debug('isConnected()')
        return True

    def init(self):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        print_debug('init()')

        self._width = 512
        self._height = 512

        return True

    def loop(self):
        """
        Get fresh tracking data
        """
        print_debug('loop()')

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

