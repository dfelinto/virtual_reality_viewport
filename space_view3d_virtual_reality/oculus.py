class Oculus():
    def __init__(self, camera, report):
        self._report = report
        self._available = True
        self._hmd = None
        self._description = None
        self._camera = camera
        self._version = 2 # DK2 by default

        self._matrix_world = camera.matrix_world.copy()
        self._lens = camera.data.lens

        self._checkModule()
        self._start()

    def isAvailable(self):
        return self._available

    def _checkModule(self):
        """if library exists append it to sys.path"""
        import sys
        import os

        addon_path = os.path.dirname(os.path.abspath(__file__))
        oculus_path = os.path.join(addon_path, "lib", "python-ovrsdk")

        if oculus_path not in sys.path:
            sys.path.append(oculus_path)

    def _start(self):
        try:
            from time import sleep
            from oculusvr import (
                    Hmd,
                    cast,
                    POINTER,
                    ovrHmdDesc,
                    ovrVector3f,
                    )

            Hmd.initialize()
            sleep(0.5)

        except SystemError as err:
            self._error("Oculus initialization failed, check the physical connections and run again")
            return

        if Hmd.detect() == 1:
            self._hmd = Hmd()
            self._description = cast(self._hmd.hmd, POINTER(ovrHmdDesc)).contents
            self._frame = 0
            self._eyes_offset = [ ovrVector3f(), ovrVector3f() ]
            self._eyes_offset[0] = 0.0, 0.0, 0.0
            self._eyes_offset[1] = 0.0, 0.0, 0.0

            self._hmd.configure_tracking()
            self._setVersion(self._description.ProductName)
            self._camera.data.lens = 16

        else:
            self._error("Oculus not connected")

    def _error(self, message):
        self._report({'ERROR'}, message)
        self._available = False

    def update(self):
        # update the camera
        matrix = self._getMatrix()

        if not matrix:
            return

        self._camera.matrix_world =  self._matrix_world * matrix

    def quit(self):
        from oculusvr import Hmd

        if self._camera:
            self._camera.matrix_world = self._matrix_world
            self._camera.data.lens = self._lens

        if Hmd.detect() == 1:
            self._hmd.destroy()
            self._hmd = None
            Hmd.shutdown()

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

            poses = self._hmd.get_eye_poses(self._frame, self._eyes_offset)

            # oculus may be returning the matrix for both eyes
            # but we are using a single eye without offset

            rotation_raw = poses[0].Orientation.toList()
            position_raw = poses[0].Position.toList()

            rotation = Quaternion(rotation_raw).to_matrix().to_4x4()
            position = Matrix.Translation(position_raw)

            matrix = position * rotation
            return matrix

        return None
