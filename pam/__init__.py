"""Parametrical Anatomical Mapping for Blender"""

import logging

import bpy

from . import gui
from . import utils
from . import tools
from . import pam_anim

logger = logging.getLogger(__name__)

bl_info = {
    "name": "PAM",
    "author": "Sebastian Klatt, Martin Pyka",
    "version": (0, 2, 0),
    "blender": (2, 7, 0),
    "license": "GPL v2",
    "description": "Parametric Anatomical Modeling is a method to translate "
                   "large-scale anatomical data into spiking neural networks.",
    "category": "Object"
}

__author__ = bl_info['author']
__license__ = bl_info['license']
__version__ = ".".join([str(s) for s in bl_info['version']])


def register():
    """Called on enabling this addon"""
    bpy.utils.register_class(gui.PAMPreferencesPane)
    utils.log.initialize()

    tools.measure.register()
    tools.visual.register()

    # PAM Anim

    pam_anim.tools.animationTools.register()
    pam_anim.tools.dataTools.register()
    pam_anim.tools.materialTools.register()
    pam_anim.tools.meshTools.register()
    pam_anim.tools.orientationTools.register()

    pam_anim.pam_anim.register()

    # Pam Anim end

    bpy.utils.register_module(__name__)
    logger.debug("Registering addon")


def unregister():
    """Called on disabling this addon"""
    tools.measure.unregister()
    tools.visual.unregister()

    bpy.utils.unregister_module(__name__)
    logger.debug("Unregistering addon")


if __name__ == "__main__":
    register()
