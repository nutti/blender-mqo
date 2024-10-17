bl_info = {
    "name": "MQO (Metasequoia) Format File Importer/Exporter",
    "author": "nutti, sapper-trle",
    "version": (2, 0, 0),
    "blender": (4, 2, 0),
    "location": "",
    "description": "Import/Export MQO format files",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "https://github.com/nutti/blender-mqo",
    "category": "Import-Export"
}


if "bpy" in locals():
    import importlib
    # pylint: disable=E0601
    importlib.reload(utils)
    utils.bl_class_registry.BlClassRegistry.cleanup()
    importlib.reload(preferences)
    importlib.reload(ops)
else:
    import bpy
    from . import utils
    from . import preferences
    from . import ops


def register():
    utils.addon_updater.register_updater()   # extensions.blender.org: Delete line  # noqa
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
