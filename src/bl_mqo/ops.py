import bmesh
import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
)
from mathutils import Vector
from bpy_extras.io_utils import ImportHelper, ExportHelper

from .utils.mqo_file import MqoFile
from .utils.bl_class_registry import BlClassRegistry
from .utils import compatibility as compat


def import_mqo_file(filepath, objects_to_import, materials_to_import, add_import_prefix):
    mqo_file = MqoFile()
    mqo_file.load(filepath)

    orig_mode = bpy.context.mode
    if orig_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    imported_prefix = "[Imported] " if add_import_prefix else ""

    materials = []
    for mqo_mtrl in mqo_file.get_materials():
        if mqo_mtrl.name not in materials_to_import:
            materials.append(None)
        else:
            # construct material
            new_mtrl = bpy.data.materials.new("{}{}".format(imported_prefix, mqo_mtrl.name))
            new_mtrl.diffuse_color = Vector((mqo_mtrl.diffuse, mqo_mtrl.diffuse, mqo_mtrl.diffuse, mqo_mtrl.diffuse))
            new_mtrl.specular_color = Vector((mqo_mtrl.specular, mqo_mtrl.specular, mqo_mtrl.specular))
            materials.append(new_mtrl)

    for mqo_obj in mqo_file.get_objects():
        if mqo_obj.name not in objects_to_import:
            continue
        # construct object
        new_mesh = bpy.data.meshes.new("{}{}".format(imported_prefix, mqo_obj.name))
        new_obj = bpy.data.objects.new("{}{}".format(imported_prefix, mqo_obj.name), new_mesh)
        new_obj.location = Vector(mqo_obj.translation)
        new_obj.rotation_euler = Vector(mqo_obj.rotation)
        new_obj.scale = Vector(mqo_obj.scale)
        bpy.context.scene.collection.objects.link(new_obj)
        bpy.context.view_layer.objects.active = new_obj
        new_obj.select_set(True)

        # construct material
        for mtrl in materials:
            bpy.ops.object.material_slot_add()
            if mtrl is not None:
               new_obj.material_slots[len(new_obj.material_slots) - 1].material = mtrl

        # construct mesh
        new_mesh = bpy.context.object.data
        bm = bmesh.new()

        # create UV map
        if bm.loops.layers.uv.items():
            uv_layer = bm.loops.layers.uv[0]
        else:
            uv_layer = bm.loops.layers.uv.new()

        bm_verts = [bm.verts.new(v) for v in mqo_obj.vertices]
        bm_faces = []
        for face in mqo_obj.faces:
            face_verts = []

            # create face
            for j in range(face.ngons):
                face_verts.append(bm_verts[face.vertex_indices[j]])
            bm_face = bm.faces.new(face_verts)

            # set UV if exists
            if face.uv_coords is not None:
                for j in range(face.ngons):
                    bm_face.loops[j][uv_layer].uv = face.uv_coords[j]

            bm_faces.append(bm_face)

        bm.to_mesh(new_mesh)
        bm.free()

        # object mode -> edit mode
        bpy.ops.object.editmode_toggle()

        mtrl_map = {}
        for i, face in enumerate(mqo_obj.faces):
            mtrl_idx = face.material
            if mtrl_idx is None:
                continue
            if mtrl_idx not in mtrl_map:
                mtrl_map[mtrl_idx] = []
            mtrl_map[mtrl_idx].append(i)

        for mtrl_idx in mtrl_map.keys():
            bm = bmesh.from_edit_mesh(new_obj.data)
            bm.faces.ensure_lookup_table()
            # set material
            for face in bm.faces:
                face.select = False
            for face_idx in mtrl_map[mtrl_idx]:
                bm.faces[face_idx].select = True
            bmesh.update_edit_mesh(new_obj.data)
            new_obj.active_material_index = mtrl_idx
            new_obj.active_material = materials[mtrl_idx]    # if material is not imported, this means to assign None
            bpy.ops.object.material_slot_assign()

        bm = bmesh.from_edit_mesh(new_obj.data)
        bm.faces.ensure_lookup_table()
        for face in bm.faces:
            face.select = False
        bmesh.update_edit_mesh(new_obj.data)

    bpy.ops.object.mode_set(mode=orig_mode)


def export_mqo_file(filepath, objects_to_export, materials_to_export, add_export_prefix):
    mqo_file = MqoFile()
    mqo_file.version = "1.1"
    mqo_file.format = "Text"

    scene = MqoFile.Scene()
    scene.set_default_params()
    mqo_file.scene = scene

    export_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    export_materials = [mtrl for mtrl in bpy.data.materials]
    exported_prefix = "[Exported] " if add_export_prefix else ""

    orig_mode = bpy.context.mode
    if orig_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # materials
    for mtrl in export_materials:
        if mtrl.name not in materials_to_export:
            continue
        mqo_mtrl = MqoFile.Material()
        mqo_mtrl.name = "{}{}".format(exported_prefix, mtrl.name)
        color = [c for c in mtrl.diffuse_color]
        mqo_mtrl.diffuse = max(color) / len(color)
        specular = [c for c in mtrl.specular_color]
        mqo_mtrl.specular = max(specular) / len(specular)
        mqo_file.materials.append(mqo_mtrl)

    # object mode -> edit mode
    bpy.ops.object.editmode_toggle()

    # objects
    for obj in export_objects:
        if obj.name not in objects_to_export:
            continue
        mqo_obj = MqoFile.Object()
        mqo_obj.name = "{}{}".format(exported_prefix, obj.name)
        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.verify()

        # vertices
        mqo_obj.vertices = [[v.co[0], v.co[1], v.co[2]] for v in bm.verts]

        # faces
        for face in bm.faces:
            mqo_face = MqoFile.Object.Face()
            mqo_face.ngons = len(face.verts)
            mqo_face.vertex_indices = [v.index for v in face.verts]
            for l in face.loops:
                if mqo_face.uv_coords is None:
                    mqo_face.uv_coords = []
                mqo_face.uv_coords.append([l[uv_layer].uv[0], l[uv_layer].uv[1]])
            mqo_obj.faces.append(mqo_face)

        # materials
        for mtrl_idx, mtrl_slot in enumerate(obj.material_slots):
            if mtrl_slot.material.name not in materials_to_export:
                continue   # does not export material index

            bm = bmesh.from_edit_mesh(obj.data)
            bm.faces.ensure_lookup_table()
            # set material
            for face in bm.faces:
                face.select = False
            bmesh.update_edit_mesh(obj.data)

            mtrl = mtrl_slot.material
            obj.active_material_index = mtrl_idx
            obj.active_material = mtrl
            bpy.ops.object.material_slot_select()

            # find material index for mqo
            mqo_mtrl_idx = -1
            for i, mqo_mtrl in enumerate(mqo_file.materials):
                if mtrl.name == mqo_mtrl.name:
                    mqo_mtrl_idx = i
                    break

            for bm_face, mqo_face in zip(bm.faces, mqo_obj.faces):
                if bm_face.select:
                    mqo_face.material = mqo_mtrl_idx

        mqo_file.objects.append(mqo_obj)

    mqo_file.save(filepath)
    bpy.ops.object.mode_set(mode=orig_mode)


@compat.make_annotations
class BoolPropertyCollection(bpy.types.PropertyGroup):
    checked = BoolProperty(name="", default=True)


@BlClassRegistry()
@compat.make_annotations
class BLMQO_OT_ImportMqo(bpy.types.Operator, ImportHelper):

    bl_idname = "uv.blmqo_ot_import_mqo"
    bl_label = "Import Metasequoia file (.mqo)"
    bl_description = "Import a Metasequoia file"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".mqo"
    filter_glob = StringProperty(default="*.mqo")

    import_objects = BoolProperty(name="Import Objects", default=True)
    import_materials = BoolProperty(name="Import Materials", default=True)
    add_import_prefix = BoolProperty(name="Add Import Prefix", default=True)
    import_prefix = StringProperty(name="Prefix", default="[Imported] ")

    bool_prop_collection = CollectionProperty(type=BoolPropertyCollection)
    objects_to_import = []
    materials_to_import = []
    loaded_file = ""

    def draw(self, context):
        layout = self.layout

        if self.loaded_file != self.properties.filepath:
            mqo_file = MqoFile()
            try:
                mqo_file.load(self.properties.filepath)
                loaded = True
            except:
                loaded = False

            self.objects_to_import = []
            self.materials_to_import = []
            self.bool_prop_collection.clear()
            if loaded:
                for obj in mqo_file.objects:
                    item = self.bool_prop_collection.add()
                    self.objects_to_import.append({"name": obj.name, "item": item})
                for mtrl in mqo_file.materials:
                    item = self.bool_prop_collection.add()
                    self.materials_to_import.append({"name": mtrl.name, "item": item})
            self.loaded_file = self.properties.filepath

        layout.label(text="File: {}".format(self.loaded_file))

        layout.prop(self, "import_objects")
        if self.import_objects and len(self.objects_to_import) > 0:
            sp = compat.layout_split(layout, factor=0.01)
            sp.column()     # spacer
            sp = compat.layout_split(sp, factor=1.0)
            col = sp.column()
            box = col.box()
            for d in self.objects_to_import:
                box.prop(d["item"], "checked", text=d["name"])

        layout.prop(self, "import_materials")
        if self.import_materials and len(self.materials_to_import) > 0:
            sp = compat.layout_split(layout, factor=0.01)
            sp.column()  # spacer
            sp = compat.layout_split(sp, factor=1.0)
            col = sp.column()
            box = col.box()
            for m in self.materials_to_import:
                box.prop(m["item"], "checked", text=m["name"])

        layout.prop(self, "add_import_prefix")
        if self.add_import_prefix:
            layout.prop(self, "import_prefix")

    def execute(self, context):
        import_objects = [o["name"] for o in self.objects_to_import if o["item"].checked == True]
        import_materials = [m["name"] for m in self.materials_to_import if m["item"].checked == True]
        import_mqo_file(self.properties.filepath, import_objects, import_materials, self.add_import_prefix)

        self.report({'INFO'}, "Imported from {}".format(self.properties.filepath))

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}


@BlClassRegistry()
@compat.make_annotations
class BLMQO_OT_ExportMqo(bpy.types.Operator, ExportHelper):

    bl_idname = "uv.blmqo_ot_export_mqo"
    bl_label = "Export Metasequoia file (.mqo)"
    bl_description = "Export a Metasequoia file"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".mqo"
    filter_glob = StringProperty(default="*.mqo")

    export_objects = BoolProperty(name="Export Objects", default=True)
    export_materials = BoolProperty(name="Export Materials", default=True)
    add_export_prefix = BoolProperty(name="Add Export Prefix", default=True)
    export_prefix = StringProperty(name="Prefix", default="[Export] ")

    bool_prop_collection = CollectionProperty(type=BoolPropertyCollection)
    objects_to_export = []
    materials_to_export = []
    initialized = False

    def draw(self, context):
        layout = self.layout

        if not self.initialized:
            self.objects_to_export = []
            self.materials_to_export = []
            self.bool_prop_collection.clear()
            for obj in bpy.data.objects:
                if obj.type != 'MESH':
                    continue
                item = self.bool_prop_collection.add()
                self.objects_to_export.append({"name": obj.name, "item": item})
            for mtrl in bpy.data.materials:
                item = self.bool_prop_collection.add()
                self.materials_to_export.append({"name": mtrl.name, "item": item})
            self.initialized = True

        layout.prop(self, "export_objects")
        if self.export_objects and len(self.objects_to_export) > 0:
            sp = compat.layout_split(layout, factor=0.01)
            sp.column()     # spacer
            sp = compat.layout_split(sp, factor=1.0)
            col = sp.column()
            box = col.box()
            for d in self.objects_to_export:
                box.prop(d["item"], "checked", text=d["name"])

        layout.prop(self, "export_materials")
        if self.export_materials and len(self.materials_to_export) > 0:
            sp = compat.layout_split(layout, factor=0.01)
            sp.column()  # spacer
            sp = compat.layout_split(sp, factor=1.0)
            col = sp.column()
            box = col.box()
            for m in self.materials_to_export:
                box.prop(m["item"], "checked", text=m["name"])

        layout.prop(self, "add_export_prefix")
        if self.add_export_prefix:
            layout.prop(self, "export_prefix")

    def execute(self, context):
        export_objects = [o["name"] for o in self.objects_to_export if o["item"].checked == True]
        export_materials = [m["name"] for m in self.materials_to_export if m["item"].checked == True]
        export_mqo_file(self.properties.filepath, export_objects, export_materials, self.add_export_prefix)

        self.report({'INFO'}, "Exported to {}".format(self.properties.filepath))

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}


def topbar_mt_file_import_fn(self, _):
    layout = self.layout

    layout.operator(BLMQO_OT_ImportMqo.bl_idname,
                    text="Metasequoia (.mqo)",
                    icon='PLUGIN')


def topbar_mt_file_export_fn(self, _):
    layout = self.layout

    layout.operator(BLMQO_OT_ExportMqo.bl_idname,
                    text="Metasequoia (.mqo)",
                    icon='PLUGIN')
