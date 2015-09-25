"""
Debug
=====

Debug device for testing
"""

from . import HMD_Data

class Debug:
    def __init__(self):
        self._device = None

    def isConnected(self):
        """
        Check if device is connected

        :return: return True if the device is connected
        :rtype: bool
        """
        print('Debug:isConnected()')
        return True

    def init(self):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        print('Debug:init()')
        return True

    def loop(self):
        """
        Get fresh tracking data
        """
        print('Debug:loop()')

    def frameReady(self):
        """
        The frame is ready to be send to the device
        """
        print('Debug:frameReady()')

    def quit(self):
        """
        Garbage collection
        """
        print('Debug:quit()')

