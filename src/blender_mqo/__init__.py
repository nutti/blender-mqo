bl_info = {
    "name": "MQO (Metasequoia) format",
    "author": "nutti, sapper-trle",
    "version": (1, 3, 0),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Import/Export MQO files",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "https://github.com/nutti/blender-mqo",
    "category": "Import-Export"
}


if "bpy" in locals():
    import importlib
    importlib.reload(utils)
    utils.bl_class_registry.BlClassRegistry.cleanup()
    importlib.reload(preferences)
    importlib.reload(ops)
else:
    import bpy
    from . import utils
    from . import preferences
    from . import ops

import os


def register_updater(bl_info):
    config = utils.addon_updater.AddonUpdatorConfig()
    config.owner = "nutti"
    config.repository = "blender-mqo"
    config.current_addon_path = os.path.dirname(os.path.realpath(__file__))
    config.branches = ["master", "develop"]
    config.addon_directory = config.current_addon_path[:config.current_addon_path.rfind(utils.addon_updater.get_separator())]
    config.min_release_version = bl_info["version"]
    config.target_addon_path = "src/blender_mqo"
    updater = utils.addon_updater.AddonUpdatorManager.get_instance()
    updater.init(bl_info, config)


def register():
    register_updater(bl_info)
    bpy.utils.register_class(ops.BLMQO_ObjectImportPropertyCollection)
    bpy.utils.register_class(ops.BLMQO_MaterialImportPropertyCollection)
    bpy.utils.register_class(ops.BLMQO_ObjectExportPropertyCollection)
    bpy.utils.register_class(ops.BLMQO_MaterialExportPropertyCollection)
    bpy.utils.register_class(ops.BLMQO_VertexWeightExportPropertyCollection)
    utils.bl_class_registry.BlClassRegistry.register()

    if utils.compatibility.check_version(2, 80, 0) >= 0:
        file_import_menu_type = bpy.types.TOPBAR_MT_file_import
        file_export_menu_type = bpy.types.TOPBAR_MT_file_export
    else:
        file_import_menu_type = bpy.types.INFO_MT_file_import
        file_export_menu_type = bpy.types.INFO_MT_file_export

    file_import_menu_type.append(ops.topbar_mt_file_import_fn)
    file_export_menu_type.append(ops.topbar_mt_file_export_fn)


def unregister():
    if utils.compatibility.check_version(2, 80, 0) >= 0:
        file_import_menu_type = bpy.types.TOPBAR_MT_file_import
        file_export_menu_type = bpy.types.TOPBAR_MT_file_export
    else:
        file_import_menu_type = bpy.types.INFO_MT_file_import
        file_export_menu_type = bpy.types.INFO_MT_file_export

    file_export_menu_type.remove(ops.topbar_mt_file_export_fn)
    file_import_menu_type.remove(ops.topbar_mt_file_import_fn)

    bpy.utils.unregister_class(ops.BLMQO_VertexWeightExportPropertyCollection)
    bpy.utils.unregister_class(ops.BLMQO_MaterialExportPropertyCollection)
    bpy.utils.unregister_class(ops.BLMQO_ObjectExportPropertyCollection)
    bpy.utils.unregister_class(ops.BLMQO_MaterialImportPropertyCollection)
    bpy.utils.unregister_class(ops.BLMQO_ObjectImportPropertyCollection)
    utils.bl_class_registry.BlClassRegistry.unregister()


if __name__ == "__main__":
    register()