import bpy
from bpy.props import (
    IntProperty,
    BoolProperty,
)

from .utils.bl_class_registry import BlClassRegistry
from .utils import compatibility as compat


@BlClassRegistry()
@compat.make_annotations
class BLMQO_Preferences(bpy.types.AddonPreferences):
    bl_idname = "blender_mqo"

    # for Config.
    selective_import = BoolProperty(
        name="Selective Import",
        description="Enable to import only selected objects and materials",
        default=False
    )
    importable_objects_limit = IntProperty(
        name="Importable Objects Limit",
        description="Limit number of objects to import",
        default=1000,
        max=10000,
        min=10
    )
    importable_materials_limit = IntProperty(
        name="Importable Materials Limit",
        description="Limit number of materials to import",
        default=1000,
        max=10000,
        min=10
    )

    def draw(self, _):
        layout = self.layout

        layout.prop(self, "selective_import")
        sp = compat.layout_split(layout, factor=0.5)
        col = sp.column()
        col.prop(self, "importable_objects_limit")
        col.prop(self, "importable_materials_limit")
        col.enabled = self.selective_import
