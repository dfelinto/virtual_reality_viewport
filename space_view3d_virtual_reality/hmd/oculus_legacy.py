"""
Oculus Legacy
=============

Oculus (oculus.com) head mounted display
It uses a C app to connect with the SDK

The bridge code is hosted at Visgraf:
http://git.impa.br/dfelinto/oculus_sdk_bridge
"""

from . import HMD_Base

from .oculus import Oculus

from ..lib import (
        checkModule,
        )

TODO = True

class OculusLegacy(Oculus):
    def __init__(self, context, error_callback):
        HMD_Base.__init__(self, 'Oculus Legacy', context, error_callback)
        checkModule('python-ovrsdk')
        self._version = 2 # DK 2 by default

    def _getHMDClass(self):
        return HMD

    def _setVersion(self, product_name):
        try:
            if product_name.find(b'DK2') != -1:
                self._version = 2

            elif product_name.find(b'DK1') != -1:
                self._version = 1

            else:
                raise Exception

        except:
            print("Error guessing device version (\"{0}\")".format(product_name))

    @property
    def shader_file(self):
        if self._version == 1:
            return 'oculus_dk1.glsl'
        else:
            return 'oculus_dk2.glsl'

    def _getMatrix(self):
        from oculusvr import Hmd
        from mathutils import (
                Quaternion,
                Matrix,
                )

        if self._hmd and Hmd.detect() == 1:
            self._frame += 1

            poses = self._hmd.get_eye_poses(self._frame, self._eyesOffset)

            # oculus may be returning the matrix for both eyes
            # but we are using a single eye without offset

            rotation_raw = poses[0].Orientation.toList()
            position_raw = poses[0].Position.toList()

            # take scene units into consideration
            position_raw = self._scaleMovement(position_raw)

            rotation = Quaternion(rotation_raw).to_matrix().to_4x4()
            position = Matrix.Translation(position_raw)

            matrix = position * rotation
            return matrix

        return None


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

        except Exception as E:
            raise E

    def __del__(self):
        import oculusvr as ovr

        if self._device:
            self._device.destroy()
            self._device = None
            ovr.Hmd.shutdown()
        TODO

    def _updateProjectionMatrix(self, near, far):
        import oculusvr as ovr

        self.projection_matrix_left = ovr.Hmd.get_perspective(self._fovPorts[0], near, far, True).toList()
        self.projection_matrix_right = ovr.Hmd.get_perspective(self._fovPorts[1], near, far, True).toList()

    def setup(self, framebuffer_left, framebuffer_right):
        """
        Initialize device

        :param framebuffer_object_left: framebuffer object created externally
        :type framebuffer_object_left: GLuint
        :param framebuffer_object_right: framebuffer object created externally
        :type framebuffer_object_right: GLuint
        :return: return True if the device was properly initialized
        :rtype: bool
        """
        return TODO

    def update(self):
        """
        Get fresh tracking data

        :return: return left orientation, left_position, right_orientation, right_position
        :rtype: tuple(list(4), list(3), list(4), list(3))
        """
        self._frame += 1
        poses = self._device.get_eye_poses(self._frame, self._eyeOffsets)
        for eye in range(2):
            self._orientation[eye] = poses[eye].Orientation.toList()
            self._position[eye] = poses[eye].Position.toList()

        return super(HMD, self).update()

    def frameReady(self):
        """
        The frame is ready to be send to the device

        :return: return True if success
        :rtype: bool
        """
        return TODO

    def reCenter(self):
        """
        Re-center the HMD device

        :return: return True if success
        :rtype: bool
        """
        self._device.recenter_pose()
        return True

