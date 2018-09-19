"""
HTC Vive
========

HTC Vive (vive.com) head mounted display
It uses a C app to connect with the SDK
"""

from .backend import HMD as baseHMD

class HMD(baseHMD):
    _name = 'HTC Vive'
    _is_direct_mode = True

    def _getHMDClass(self):
        from bridge.hmd.openvr import HMD
        return HMD

