"""
Oculus
======

Oculus (oculus.com) head mounted display
It uses a C app to connect with the SDK

The bridge code is hosted at Visgraf:
http://git.impa.br/dfelinto/oculus_sdk_bridge
"""

TODO = True

from . import HMD_Data

class Oculus:
    def __init__(self):
        self._device = None

    def isConnected(self):
        """
        Check if device is connected

        :return: return True if the device is connected
        :rtype: bool
        """
        TODO
        """
        Oculus SDK bridge

        return: true/false
        """

    def init(self):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        TODO
        """
        Oculus SDK bridge

        return: status, fbo, texture, projection matrix, eye separation, width, height
        """

    def loop(self):
        """
        Get fresh tracking data
        """
        TODO
        """
        Oculus SDK bridge

        return:head position, head orientation
        """

    def frameReady(self):
        """
        The frame is ready to be send to the device
        """
        TODO
        """
        Oculus SDK bridge
        """

    def quit(self):
        """
        Garbage collection
        """
        TODO
        """
        Oculus SDK bridge

        delete fbo, rbo, tex_id
        """

