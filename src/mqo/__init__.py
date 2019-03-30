bl_info = {
    "name": "MQO (Metasequoia) format",
    "author": "Nutti",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Import/Export MQO files",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "https://github.com/nutti/bl-mqo",
    "category": "Import-Export"
}


if "bpy" in locals():
    import importlib
    importlib.reload(utils)
    utils.bl_class_registry.BlClassRegistry.cleanup()
    importlib.reload(ops)
else:
    import bpy
    from . import utils
    from . import ops


def register():

    bpy.utils.register_class(ops.BoolPropertyCollection)
    utils.bl_class_registry.BlClassRegistry.register()

    bpy.types.TOPBAR_MT_file_import.append(ops.topbar_mt_file_import_fn)
    bpy.types.TOPBAR_MT_file_export.append(ops.topbar_mt_file_export_fn)

    bpy.types.Scene.dynamic_bool_property = bpy.props.CollectionProperty(type=ops.BoolPropertyCollection)


def unregister():
    del bpy.types.Scene.dynamic_bool_property

    bpy.types.TOPBAR_MT_file_export.remove(ops.topbar_mt_file_export_fn)
    bpy.types.TOPBAR_MT_file_import.remove(ops.topbar_mt_file_import_fn)

    utils.bl_class_registry.BlClassRegistry.unregister()
    bpy.utils.unregister_class(ops.BoolPropertyCollection)


if __name__ == "__main__":
    register()