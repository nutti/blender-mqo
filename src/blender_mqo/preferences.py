import bpy
from bpy.props import (
    IntProperty,
    BoolProperty,
    StringProperty,
    EnumProperty,
)

from .utils.addon_updater import AddonUpdaterManager    # extensions.blender.org: Delete line # pylint: disable=C0301 # noqa
from .utils.bl_class_registry import BlClassRegistry
from .utils import compatibility as compat


# extensions.blender.org: Delete block start
@BlClassRegistry()
class BLMQO_OT_CheckAddonUpdate(bpy.types.Operator):
    bl_idname = "import_scene.blmqo_check_addon_update"
    bl_label = "Check Update"
    bl_description = "Check Add-on Update"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, _):
        updater = AddonUpdaterManager.get_instance()
        updater.check_update_candidate()

        return {'FINISHED'}


@BlClassRegistry()
@compat.make_annotations
class BLMQO_OT_UpdateAddon(bpy.types.Operator):
    bl_idname = "import_scene.blmqo_update_addon"
    bl_label = "Update"
    bl_description = "Update Add-on"
    bl_options = {'REGISTER', 'UNDO'}

    branch_name = StringProperty(
        name="Branch Name",
        description="Branch name to update",
        default="",
    )

    def execute(self, _):
        updater = AddonUpdaterManager.get_instance()
        updater.update(self.branch_name)

        return {'FINISHED'}


def get_update_candidate_branches(_, __):
    updater = AddonUpdaterManager.get_instance()
    if not updater.candidate_checked():
        return []

    return [(name, name, "") for name in updater.get_candidate_branch_names()]
# extensions.blender.org: Delete block end


@BlClassRegistry()
@compat.make_annotations
class BLMQO_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

# extensions.blender.org: Delete block start
    # for add-on updater
    updater_branch_to_update = EnumProperty(
        name="branch",
        description="Target branch to update add-on",
        items=get_update_candidate_branches
    )
# extensions.blender.org: Delete block end

    # for UI.
    category = EnumProperty(
        name="Category",
        description="Preferences Category",
        items=[
            ('CONFIG', "Configuration", "Configuration about this add-on"),
            ('UPDATE', "Update", "Update this add-on"),     # extensions.blender.org: Delete line  # pylint: disable=C0301 # noqa
        ],
        default='CONFIG'
    )

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

        layout.row().prop(self, "category", expand=True)

        if self.category == 'CONFIG':
            layout.separator()

            layout.prop(self, "selective_import")
            sp = compat.layout_split(layout, factor=0.5)
            col = sp.column()
            col.prop(self, "importable_objects_limit")
            col.prop(self, "importable_materials_limit")
            col.enabled = self.selective_import

# extensions.blender.org: Delete block start
        elif self.category == 'UPDATE':
            updater = AddonUpdaterManager.get_instance()

            layout.separator()

            if not updater.candidate_checked():
                col = layout.column()
                col.scale_y = 2
                row = col.row()
                row.operator(BLMQO_OT_CheckAddonUpdate.bl_idname,
                             text="Check 'blender-mqo' add-on update",
                             icon='FILE_REFRESH')
            else:
                row = layout.row(align=True)
                row.scale_y = 2
                col = row.column()
                col.operator(BLMQO_OT_CheckAddonUpdate.bl_idname,
                             text="Check 'blender-mqo' add-on update",
                             icon='FILE_REFRESH')
                col = row.column()
                if updater.latest_version() != "":
                    col.enabled = True
                    ops = col.operator(
                        BLMQO_OT_UpdateAddon.bl_idname,
                        text="""Update to the latest release version
                        (version: {})"""
                        .format(updater.latest_version()),
                        icon='TRIA_DOWN_BAR')
                    ops.branch_name = updater.latest_version()
                else:
                    col.enabled = False
                    col.operator(BLMQO_OT_UpdateAddon.bl_idname,
                                 text="No updates are available.")

                layout.separator()
                layout.label(text="Manual Update:")
                row = layout.row(align=True)
                row.prop(self, "updater_branch_to_update", text="Target")
                ops = row.operator(
                    BLMQO_OT_UpdateAddon.bl_idname, text="Update",
                    icon='TRIA_DOWN_BAR')
                ops.branch_name = self.updater_branch_to_update

                layout.separator()
                if updater.has_error():
                    box = layout.box()
                    box.label(text=updater.error(), icon='CANCEL')
                elif updater.has_info():
                    box = layout.box()
                    box.label(text=updater.info(), icon='ERROR')
# extensions.blender.org: Delete block end
