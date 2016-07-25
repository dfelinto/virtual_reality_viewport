"""
Oculus Legacy
=============

Oculus (oculus.com) head mounted display for OSX and Linux
It uses a python wrapper to connect with the SDK
"""

from .backend import HMD as baseHMD

class HMD(baseHMD):
    _name = 'Oculus Legacy'
    _is_direct_mode = False

    def _getHMDClass(self):
        from bridge.hmd.oculus_legacy import HMD
        return HMD

