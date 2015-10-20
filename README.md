# Virtual Reality Viewport
Addon to bring virtual reality devices to the Blender viewport.

This is work in progress, use at your own risk.

Pre-Requisite
============
* Blender 2.77 (https://builder.blender.org/download)
* Oculus 0.5 runtime

Note
====
* Windows 64 builds are not working at the moment, use 32 bits instead
* Extended Mode is the only supported mode

How to Use
==========
In the viewport go to the toolshelf, select the ``Virtual Reality`` tab, click on the ``Virtual Reality`` button and follow the on-screen instructions.

Current State
=============
<img src="https://pbs.twimg.com/media/CCm5C85WYAAy2jL.jpg:large" width="600" />

Video of an old version of the plugin working:

[![Video of plugin in action](http://img.youtube.com/vi/saSn2qvW0aE/0.jpg)](https://www.youtube.com/watch?v=saSn2qvW0aE)

Oculus SDK 0.5 is working across Windows, Mac and Linux.

Easy Installation
=================
You can get the latest version of the Addon here:
http://www.dalaifelinto.com/ftp/builds/space_view3d_virtual_reality.zip

Advanced Installation
=====================
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
* Oculus SDK 0.7 is still in progress.
* Later we can also extend the external bridge library to support other HMD devices.

Credits
=======
* Oculus SDK 0.5 wrapper by https://github.com/jherico/python-ovrsdk
* Oculus SDK 0.7 bridge: Dalai Felinto and Djalma Lucio @ Visgraf / IMPA 
* Blender Addon - Dalai Felinto - http://www.dalaifelinto.com

Acknowledgements
================
* Visgraf / IMPA - for supporting the core of the addon development
* Campbell Barton - for reviewing and contributing to the patches for Blender core
* Thanks for all the testers
