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
        HMD_Base.__init__(self, 'Oculus Legacy', context, error_callback)
        checkModule('python-ovrsdk')

    def _getHMDClass(self):
        return HMD

    def _setup(self):
        return self._hmd.setup(self._color_object[0], self._color_object[1])


checkModule('oculus_sdk_bridge')
from bridge.hmd import HMD as wrapperHMD

class HMD(wrapperHMD):
    def __init__(self):
        super(HMD, self).__init__()

        import oculusvr as ovr
        from oculusvr import Hmd, ovrGLTexture, ovrPosef, ovrVector3f
        from time import sleep

        try:
            Hmd.initialize()
            sleep(0.5)

        except SystemError as err:
            self.error("__init__", Exception("Oculus initialization failed, check the physical connections and run again", True))
            return

        try:
            debug = not Hmd.detect()
            self._device = Hmd(debug=debug)

            desc = self._device.hmd.contents
            self._frame = -1

            sleep(0.1)
            self._device.configure_tracking()

            self._fovPorts = (
                desc.DefaultEyeFov[0],
                desc.DefaultEyeFov[1],
                )

            self._eyeTextures = [ ovrGLTexture(), ovrGLTexture() ]
            self._eyeOffsets = [ ovrVector3f(), ovrVector3f() ]

            rc = ovr.ovrRenderAPIConfig()
            header = rc.Header
            header.API = ovr.ovrRenderAPI_OpenGL
            header.BackBufferSize = desc.Resolution
            header.Multisample = 1

            for i in range(8):
                rc.PlatformData[i] = 0

            self._eyeRenderDescs = self._device.configure_rendering(rc, self._fovPorts)

            for eye in range(2):
                size = self._device.get_fov_texture_size(eye, self._fovPorts[eye])
                self._width[eye], self._height[eye] = size.w, size.h
                eyeTexture = self._eyeTextures[eye]
                eyeTexture.API = ovr.ovrRenderAPI_OpenGL
                header = eyeTexture.Texture.Header
                header.TextureSize = size
                vp = header.RenderViewport
                vp.Size = size
                vp.Pos.x = 0
                vp.Pos.y = 0

                self._eyeOffsets[eye] = self._eyeRenderDescs[eye].HmdToEyeViewOffset

            # Bug in the SDK leaves a program bound, so clear it
            import bgl
            bgl.glUseProgram(0)

        except Exception as E:
            raise E

    def __del__(self):
        import oculusvr as ovr

        if self._device:
            self._device.destroy()
            self._device = None
            ovr.Hmd.shutdown()

    def _updateProjectionMatrix(self, near, far):
        import oculusvr as ovr

        self.projection_matrix_left = ovr.Hmd.get_perspective(self._fovPorts[0], near, far, True).toList()
        self.projection_matrix_right = ovr.Hmd.get_perspective(self._fovPorts[1], near, far, True).toList()

    def setup(self, color_left, color_right):
        """
        Initialize device

        :param color_object_left: color object created externally
        :type color_object_left: GLuint
        :param color_object_right: color object created externally
        :type color_object_right: GLuint
        :return: return True if the device was properly initialized
        :rtype: bool
        """
        import oculusvr as ovr

        # disable safety warning
        ovr.ovrHmd_DismissHSWDisplay(self._device.hmd)

        self._eyeTextures[0].OGL.TexId = color_left
        self._eyeTextures[1].OGL.TexId = color_right
        return True

    def update(self):
        """
        Get fresh tracking data

        :return: return left orientation, left_position, right_orientation, right_position
        :rtype: tuple(list(4), list(3), list(4), list(3))
        """
        self._frame += 1
        poses = self._device.get_eye_poses(self._frame, self._eyeOffsets)

        self._device.begin_frame(self._frame)

        for eye in range(2):
            self._orientation[eye] = poses[eye].Orientation.toList()
            self._position[eye] = poses[eye].Position.toList()

        self._poses = poses
        return super(HMD, self).update()

    def frameReady(self):
        """
        The frame is ready to be send to the device

        :return: return True if success
        :rtype: bool
        """
        self._device.end_frame(self._poses, self._eyeTextures)
        return True

    def reCenter(self):
        """
        Re-center the HMD device

        :return: return True if success
        :rtype: bool
        """
        self._device.recenter_pose()
        return True

