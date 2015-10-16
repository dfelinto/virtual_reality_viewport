# Virtual Reality Viewport
Addon to bring virtual reality devices to the Blender viewport.

This is work in progress/pre-alpha state, use at your own risk.

Pre-Requisite
============

Custom Blender build from https://github.com/dfelinto/blender/tree/oculus

* Win 32: http://www.dalaifelinto.com/ftp/buids/framebuffer-win32_latest.zip
* Win 64: http://www.dalaifelinto.com/ftp/buids/framebuffer-win64_latest.zip
* OSX 64: http://www.dalaifelinto.com/ftp/buids/framebuffer-OSX-10.6-x86_64_latest.zip
* Linux 64: http://www.dalaifelinto.com/ftp/buids/framebuffer-linux-glibc211-x86_64_latest.tar.bz2

You can also get the latest version of the Addon here:
* http://www.dalaifelinto.com/ftp/buids/space_view3d_virtual_reality.zip


How to Use
==========

In the viewport go to the toolshelf, select the ``Virtual Reality`` tab, click on the ``Virtual Reality`` button and follow the on-screen instructions.

Current State
=============
<img src="https://pbs.twimg.com/media/CCm5C85WYAAy2jL.jpg:large" width="600" />

Video of plugin working:

[![Video of plugin in action](http://img.youtube.com/vi/saSn2qvW0aE/0.jpg)](https://www.youtube.com/watch?v=saSn2qvW0aE)

Oculus SDK 0.5 is working across Windows, Mac and Linux.

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
In a terminal paste the following commands:
```
$ git pull origin
$ git submodule update --recursive --remote
```

Followed by the rsync command for your OS:

Mac:
```
$ rsync -rv --exclude=.DS_Store --exclude=.git --exclude=*.blend1 --exclude=*.blend2 --exclude=*.swp --exclude=*.swo space_view3d_virtual_reality ~/Library/Application\ Support/Blender/2.76/scripts/addons/
```

Linux:
```
$ rsync -rv --exclude=.DS_Store --exclude=.git --exclude=*.blend1 --exclude=*.blend2 --exclude=*.swp --exclude=*.swo space_view3d_virtual_reality ~/.config/blender/2.76/scripts/addons/
```

Optionally, instead of rsync you can generate a new ``.zip``, remove the previous version of the addon and re-install it.

Roadmap
=======
Oculus SDK 0.7 is still in progress.

Later we can also extend the external bridge library to support other HMD devices.

Also, we need to decide how to better handle the externals (bridge and python-ovrsdk).

Credits
=======
* Oculus SDK 0.5 wrapper by https://github.com/jherico/python-ovrsdk
* Oculus SDK 0.7 bridge: Dalai Felinto and Djalma Lucio @ Visgraf / IMPA 
* Blender Addon - Dalai Felinto - http://www.dalaifelinto.com

Acknowledgements
================
Visgraf / IMPA - for supporting the core of the addon development
