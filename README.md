# Virtual Reality Viewport
Addon to bring virtual reality devices to the Blender viewport.

This is work in progress/pre-alpha state, use at your own risk.

How to Use
==========

In the viewport press ``Space`` + ``Virtual Reality Viewport``.

And then press:
* ``Alt + F11`` (Window Fullscreen)
* ``Alt + F10`` (Fullscreen Area and Hide Panels)

Current State
=============
<img src="https://pbs.twimg.com/media/CCm5C85WYAAy2jL.jpg:large" width="600" />

Installation
============
In a terminal paste the following commands:
```
$ git clone https://github.com/dfelinto/virtual_reality_viewport.git
$ cd virtual_reality_viewport
$ git submodule update --init --recursive --remote
$ zip -x __pycache__ -x */.git* -r9 space_view3d_virtual_reality.zip space_view3d_virtual_reality
```

Now install the space_view3d_virtual_reality.zip in Blender as an addon.

Update
======
The following commands are for Mac, some changes are needed for other OSs:

```
$ git pull origin
$ git submodule update --recursive --remote
$ rsync -rv --exclude=.DS_Store --exclude=.git --exclude=*.blend1 --exclude=*.blend2 --exclude=*.swp --exclude=*.swo space_view3d_virtual_reality ~/Library/Application\ Support/Blender/2.74/scripts/addons/
```

Optionally, instead of rsync you can generate a new ``.zip``, remove the previous version of the addon and re-install it.

Roadmap
=======
First and foremost I plan to suport Oculus Rift, later we can make it flexible enough to support other HMD devices.
For that the next step is to take the transformation data from the device and rotate the viewport camera.

There are a few things I still need to implement:
* Automatically go to clean fullscreen (Alt+F10) and fullwindow (Alt+F11)

Feel free to send pull requests to any of the above.

Credits
=======
Oculus DK2 Shader by Martins Upitis (which I guess based his work from elsewhere)

OculusVR wrapper by https://github.com/jherico/python-ovrsdk

Blender Addon - Dalai Felinto - http://www.dalaifelinto.com
