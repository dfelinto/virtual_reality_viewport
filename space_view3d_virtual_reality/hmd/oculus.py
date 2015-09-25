"""
Oculus
======

Oculus (oculus.com) head mounted display
It uses a C app to connect with the SDK

The bridge code is hosted at Visgraf:
http://git.impa.br/dfelinto/oculus_sdk_bridge
"""

TODO = False

from . import HMD_Data

class Oculus:
    def __init__(self):
        self.checkModule('oculus_bridge')
        self._device = None

    def isConnected(self):
        """
        Check if device is connected

        :return: return True if the device is connected
        :rtype: bool
        """
        import bridge

        try:
            return bridge.isConnected()

        except Exception as E:
            print(E)
            return False

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
        return TODO
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

    def checkModule(self, path):
        """
        If library exists append it to sys.path
        """
        import sys
        import os

        addon_path = os.path.dirname(os.path.abspath(__file__))
        library_path = os.path.join(addon_path, "lib", path)

        if library_path not in sys.path:
            sys.path.append(library_path)

