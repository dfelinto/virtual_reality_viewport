"""
Library
=======

Sorted util functions
"""

def getAddonName():
    return __name__.split('.')[0]


def getDisplayBackend(context):
    """preference set in the addon"""
    addon = getAddonName()
    preferences = context.user_preferences.addons[addon].preferences
    return preferences.display_backend


def checkModule(path):
    """
    If library exists append it to sys.path
    """
    import sys
    import os

    addon_path = os.path.dirname(os.path.abspath(__file__))
    library_path = os.path.join(addon_path, "lib", path)

    if library_path not in sys.path:
        sys.path.append(library_path)

