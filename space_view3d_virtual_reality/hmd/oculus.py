"""
Oculus
======

Oculus (oculus.com) head mounted display
It uses a C app to connect with the SDK

The bridge code is hosted at Visgraf:
http://git.impa.br/dfelinto/oculus_sdk_bridge
"""

TODO = False

from . import HMD_Base, HMD_Data

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
        from bridge import OculusBridge

        try:
            return OculusBridge.isConnected()

        except Exception as E:
            print(E)
            return False

    def init(self):
        """
        Initialize device

        :return: return True if the device was properly initialized
        :rtype: bool
        """
        return TODO
        """
        Oculus SDK bridge

        return: status, projection matrix, eye separation, width, height
        """
        return super(Oculus, self).init()

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
        return super(Oculus, self).quit()

