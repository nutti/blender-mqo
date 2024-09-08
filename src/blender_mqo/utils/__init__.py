if "bpy" in locals():
    import importlib
    # pylint: disable=E0601
    importlib.reload(mqo_file)
    importlib.reload(addon_updater)
    importlib.reload(bl_class_registry)
    importlib.reload(compatibility)
else:
    from . import mqo_file
    from . import addon_updater
    from . import bl_class_registry
    from . import compatibility

# pylint: disable=C0413
import bpy
