if "bpy" in locals():
    import importlib
    importlib.reload(mqo_file)
    importlib.reload(bl_class_registry)
    importlib.reload(compatibility)
else:
    from . import mqo_file
    from . import bl_class_registry
    from . import compatibility

import bpy