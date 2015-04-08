# Virtual Reality Viewport
Addon to bring virtual reality devices to the Blender viewport.
How to use it:

In the viewport press space + Virtual Reality Viewport.
Now press home + Alt+F11 + Alt+F10

This is WIP/Pre-Alpha state, use at your own risk.

Current State
=============
<img src="https://pbs.twimg.com/media/CCDEuQFWIAIMaEN.jpg:large" width="600" />

Roadmap
=======
First and foremost I plan to suport Oculus Rift, later we can make it flexible enough to support other HMD devices.
For that the next step is to take the transformation data from the device and rotate the viewport camera.

There are a few things I still need to implement:
* Automatically extend the view (HOME)
* Automatically go to clean fullscreen (Alt+F10) and fullwindow (Alt+F11)
* Go to the camera view (NUMPAD 0)

Feel free to send pull requests to any of the above.

Credits
=======
Oculus DK2 Shader by Martinsh Upitis (which I guess based his work from elsewhere)
OculusVR wrapper by https://github.com/jherico/python-ovrsdk
