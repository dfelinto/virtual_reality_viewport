"""
Oculus Legacy
=============

Oculus (oculus.com) head mounted display for OSX and Linux
It uses a python wrapper to connect with the SDK
"""

from . import HMD_Base

from .oculus import Oculus

from ..lib import (
        checkModule,
        )

class OculusLegacy(Oculus):
    def __init__(self, context, error_callback):
        HMD_Base.__init__(self, 'Oculus Legacy', False, context, error_callback)
        checkModule('hmd_sdk_bridge')

    def _getHMDClass(self):
        from bridge.hmd.oculus_legacy import HMD
        return HMD

    def _setup(self):
        return self._hmd.setup(self._color_object[0], self._color_object[1])
