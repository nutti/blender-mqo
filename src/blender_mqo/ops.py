import os
import pathlib
import math

import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
)
from mathutils import Vector
from bpy_extras.io_utils import ImportHelper, ExportHelper

from .utils import mqo_file as mqo
from .utils.bl_class_registry import BlClassRegistry
from .utils import compatibility as compat


MQO_TO_BLENDER_PROJECTION_TYPE = {0: 'BOX', 1: 'FLAT', 2: 'TUBE', 3: 'SPHERE'}
BLENDER_TO_MQO_PROJECTION_TYPE = {'BOX': 0, 'FLAT': 1, 'TUBE': 2, 'SPHERE': 3}
MQO_TO_BLENDER_MIRROR_TYPE = {0: 'NONE', 1: 'SEPARATE', 2: 'CONNECT'}


def get_outermost_verts(mesh, linked_face_indices, linked_edge_indices):
    outermost_verts = []
    for v in mesh.vertices:
        if len(linked_face_indices[v.index]) != \
                len(linked_edge_indices[v.index]):
            outermost_verts.append(v)
    return outermost_verts


def get_linked_face_indices(mesh):
    linked_face_indices = {v.index: [] for v in mesh.vertices}
    for face in mesh.polygons:
        for vidx in face.vertices:
            linked_face_indices[vidx].append(face.index)
    return linked_face_indices


def get_linked_edge_indices(mesh):
    linked_edge_indices = {v.index: [] for v in mesh.vertices}
    for edge in mesh.edges:
        for vidx in edge.vertices:
            linked_edge_indices[vidx].append(edge.index)
    return linked_edge_indices


def get_other_vert(mesh, edge, vert):
    other_vert_idx = None
    for vidx in edge.vertices:
        if vidx != vert.index:
            other_vert_idx = vidx
            return mesh.vertices[other_vert_idx]
    return None


def import_material_v279(mqo_mtrl, filepath):
    # construct material
    new_mtrl = bpy.data.materials.new(mqo_mtrl.name)
    new_mtrl.diffuse_color = Vector(mqo_mtrl.color[0:3])
    new_mtrl.diffuse_intensity = mqo_mtrl.diffuse
    new_mtrl.specular_color = Vector(mqo_mtrl.color[0:3])
    new_mtrl.specular_intensity = mqo_mtrl.specular
    new_mtrl.emit = mqo_mtrl.emissive
    new_mtrl.ambient = mqo_mtrl.ambient

    new_image = None
    if mqo_mtrl.texture_map is not None:
        # open image
        image_path = "{}/{}".format(os.path.dirname(filepath),
                                    mqo_mtrl.texture_map)
        new_image = bpy.data.images.load(image_path)

    return {"material": new_mtrl, "image": new_image}


def import_material_v280(mqo_mtrl, filepath):
    # construct material
    new_mtrl = bpy.data.materials.new(mqo_mtrl.name)
    new_mtrl.use_nodes = True
    output_node = next(n for n in new_mtrl.node_tree.nodes
                       if n.type == "OUTPUT_MATERIAL")

    # remove unused nodes
    nodes_to_remove = [n for n in new_mtrl.node_tree.nodes if n != output_node]
    for n in nodes_to_remove:
        new_mtrl.node_tree.nodes.remove(n)

    new_image = None
    if mqo_mtrl.texture_map is not None:
        # open image
        path = pathlib.Path(mqo_mtrl.texture_map)
        if path.is_absolute():
            image_path = str(path)
        else:
            image_path = "{}/{}".format(os.path.dirname(filepath),
                                        mqo_mtrl.texture_map)
            if not pathlib.Path(image_path).exists():
                image_path = \
                    "C:/Program Files/tetraface/Metasequoia4/Texture/" + \
                    mqo_mtrl.texture_map
        if pathlib.Path(image_path).exists():
            new_image = bpy.data.images.load(image_path)

            # make texture node
            texture_node = new_mtrl.node_tree.nodes.new("ShaderNodeTexImage")
            texture_node.location[1] = output_node.location[1]
            texture_node.image = new_image
            if mqo_mtrl.projection_type is not None:
                texture_node.projection = MQO_TO_BLENDER_PROJECTION_TYPE[
                    mqo_mtrl.projection_type]
            new_mtrl.node_tree.links.new(output_node.inputs["Surface"],
                                         texture_node.outputs["Color"])
    else:
        # make specular node
        specular_node = new_mtrl.node_tree.nodes.new("ShaderNodeEeveeSpecular")
        specular_node.location[1] = output_node.location[1]
        specular_node.inputs["Base Color"].default_value = mqo_mtrl.color
        specular_node.inputs["Specular"].default_value = [
            mqo_mtrl.specular, mqo_mtrl.specular, mqo_mtrl.specular,
            mqo_mtrl.specular
        ]
        specular_node.inputs["Emissive Color"].default_value = [
            mqo_mtrl.emissive, mqo_mtrl.emissive, mqo_mtrl.emissive,
            mqo_mtrl.emissive
        ]
        new_mtrl.node_tree.links.new(output_node.inputs["Surface"],
                                     specular_node.outputs["BSDF"])

    return {"material": new_mtrl, "image": new_image}


def import_material(mqo_mtrl, filepath):
    if compat.check_version(2, 80, 0) >= 0:
        return import_material_v280(mqo_mtrl, filepath)

    return import_material_v279(mqo_mtrl, filepath)


def import_materials(mqo_file, filepath, exclude_materials):
    materials_imported = []
    for mqo_mtrl in mqo_file.get_materials():
        if mqo_mtrl.name in exclude_materials:
            materials_imported.append({"material": None, "image": None})
        else:
            materials_imported.append(import_material(mqo_mtrl, filepath,))
    return materials_imported


def import_object(mqo_obj, materials, vertex_weight_import_options):
    # construct object
    new_mesh = bpy.data.meshes.new(mqo_obj.name)
    new_obj = bpy.data.objects.new(mqo_obj.name, new_mesh)
    new_obj.location = Vector(mqo_obj.translation)
    new_obj.rotation_euler = Vector(mqo_obj.rotation)
    new_obj.scale = Vector(mqo_obj.scale)
    if compat.check_version(2, 80, 0) >= 0:
        bpy.context.scene.collection.objects.link(new_obj)
        bpy.context.view_layer.objects.active = new_obj
        new_obj.select_set(True)
    else:
        bpy.context.scene.objects.link(new_obj)
        bpy.context.scene.objects.active = new_obj
        new_obj.select = True

    # construct material
    for mtrl in materials:
        bpy.ops.object.material_slot_add()
        if mtrl is not None:
            new_obj.material_slots[len(new_obj.material_slots) - 1]\
                .material = mtrl["material"]

    # construct mesh
    new_mesh = bpy.context.object.data
    mqo_verts = mqo_obj.get_vertices()
    mqo_faces = mqo_obj.get_faces(uniq=True)
    face_indices = [f.vertex_indices for f in mqo_faces]

    new_mesh.from_pydata(mqo_verts, [], face_indices)
    new_mesh.update(calc_edges=True)

    vertex_weights = mqo_obj.get_vertexattr('WEIT')
    vertex_weighted_vertices = {}
    if vertex_weight_import_options.import_ and vertex_weights is not None:
        for vidx, weight in vertex_weights.items():
            vertex_weighted_vertices[new_mesh.vertices[vidx]] = weight

    # make vertices and faces for mirror connection
    # pylint: disable=too-many-nested-blocks
    if mqo_obj.mirror is not None:
        if MQO_TO_BLENDER_MIRROR_TYPE[mqo_obj.mirror] == 'CONNECT':
            linked_face_indices = get_linked_face_indices(new_mesh)
            linked_edge_indices = get_linked_edge_indices(new_mesh)
            outermost_verts = get_outermost_verts(
                new_mesh, linked_face_indices, linked_edge_indices)
            outermost_vert_indices = [v.index for v in outermost_verts]

            new_verts_co = [list(v.co) for v in new_mesh.vertices]
            new_faces_indices = [list(f.vertices) for f in new_mesh.polygons]

            # make vertices aligned to axis
            axis_aligned_verts = {}
            for i, ovidx in enumerate(outermost_vert_indices):
                new_vert_co = list(new_mesh.vertices[ovidx].co)
                axis_index = mqo_obj.mirror_axis
                # TODO: Need to clarify the specification when more than two
                #       axes are specified. For now, we applied about highest
                #       prioritized axis. (X > Y > Z)
                if axis_index & 0x1:
                    new_vert_co[0] = 0.0
                elif axis_index & 0x2:
                    new_vert_co[1] = 0.0
                elif axis_index & 0x4:
                    new_vert_co[2] = 0.0
                axis_aligned_verts[ovidx] = len(new_verts_co)
                new_verts_co.append(new_vert_co)

            # make ordered outermost vertices
            rest = outermost_vert_indices
            link_groups = []
            while len(rest) != 0:
                links = []
                cur_vert_idx = rest[0]
                first_vert_idx = rest[0]
                is_vert_loop = False
                has_no_link_edge = False
                is_first_time = True
                while True:
                    rest.remove(cur_vert_idx)
                    # find adjacent vertices
                    for eidx in linked_edge_indices[cur_vert_idx]:
                        next_vert = get_other_vert(
                            new_mesh, new_mesh.edges[eidx],
                            new_mesh.vertices[cur_vert_idx])
                        if next_vert.index in rest:
                            links.append([cur_vert_idx, next_vert.index])
                            cur_vert_idx = next_vert.index
                            break
                    else:  # not found, then check if this is a vertex loop
                        for eidx in linked_edge_indices[cur_vert_idx]:
                            next_vert = get_other_vert(
                                new_mesh, new_mesh.edges[eidx],
                                new_mesh.vertices[cur_vert_idx])
                            if next_vert.index == first_vert_idx and \
                                    not is_first_time:
                                is_vert_loop = True
                                links.append([cur_vert_idx, first_vert_idx])
                                break
                        else:  # vertex has no linked edge
                            has_no_link_edge = True
                    is_first_time = False
                    if len(rest) == 0 or is_vert_loop or has_no_link_edge:
                        break
                link_groups.append(links)

            # make faces
            for lo in link_groups:
                for li in lo:
                    new_faces_indices.append([
                        li[0], li[1],
                        axis_aligned_verts[li[1]],
                        axis_aligned_verts[li[0]],
                    ])

            if compat.check_version(2, 81, 0) < 0:
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.delete(type='VERT')
                bpy.ops.object.editmode_toggle()
            else:
                new_mesh.clear_geometry()
            new_mesh.from_pydata(new_verts_co, [], new_faces_indices)
            new_mesh.update(calc_edges=True)

    # create UV map
    has_uvmap = False
    for face in mqo_faces:
        if face.uv_coords is not None:
            has_uvmap = True
    uv_layer = None
    if has_uvmap:
        if new_mesh.uv_layers.items():
            uv_layer = new_mesh.uv_layers[0]
        else:
            if compat.check_version(2, 80, 0) < 0:
                bpy.ops.mesh.uv_texture_add()
                uv_layer = new_mesh.uv_layers[0]
            else:
                uv_layer = new_mesh.uv_layers.new()

    # set UV if exists
    uv_data_idx = 0
    for face in mqo_faces:
        if face.uv_coords is not None:
            for i in range(face.ngons):
                uv_layer.data[uv_data_idx].uv = face.uv_coords[i]
                uv_layer.data[uv_data_idx].uv[1] = \
                    1 - uv_layer.data[uv_data_idx].uv[1]
                uv_data_idx += 1

    # Construct vertex groups to store vertex weights.
    if vertex_weighted_vertices:
        if vertex_weight_import_options.grouped_by == 'ALL_IN_ONE':
            vertex_weights_group = new_obj.vertex_groups.new(
                name=vertex_weight_import_options.group_name)
            for v, weight in vertex_weighted_vertices.items():
                vertex_weights_group.add([v.index], weight, 'REPLACE')
        elif vertex_weight_import_options.grouped_by == 'WEIGHT_VALUE':
            weight_to_vertices = {}
            for v, weight in vertex_weighted_vertices.items():
                if weight not in weight_to_vertices:
                    weight_to_vertices[weight] = []
                weight_to_vertices[weight].append(v)
            for i, (weight, vs) in enumerate(weight_to_vertices.items()):
                group_name = "{} {}".format(
                    vertex_weight_import_options.group_name, i)
                vertex_weights_group = new_obj.vertex_groups.new(
                    name=group_name)
                for v in vs:
                    vertex_weights_group.add([v.index], weight, 'REPLACE')

    mtrl_map = {}
    for i, face in enumerate(mqo_faces):
        mtrl_idx = face.material
        if mtrl_idx is None:
            continue
        if mtrl_idx not in mtrl_map:
            mtrl_map[mtrl_idx] = []
        mtrl_map[mtrl_idx].append(i)

    # Changing mesh select mode is required to reflect the material
    # assignments.
    mesh_select_mode_orig = list(bpy.context.tool_settings.mesh_select_mode)
    bpy.context.tool_settings.mesh_select_mode = (False, False, True)

    for mtrl_idx, face_indices in mtrl_map.items():
        # Face selection must be done in object mode requires to switch to
        # edit mode.
        for face in new_mesh.polygons:
            face.select = False
        for face_idx in face_indices:
            new_mesh.polygons[face_idx].select = True

        bpy.ops.object.editmode_toggle()    # object mode -> edit mode

        new_obj.active_material_index = mtrl_idx
        # if material is not imported, this means to assign None
        new_obj.active_material = materials[mtrl_idx]["material"]
        bpy.ops.object.material_slot_assign()

        bpy.ops.object.editmode_toggle()    # edit mode -> object mode

    bpy.context.tool_settings.mesh_select_mode = mesh_select_mode_orig

    # Set texture images.
    if has_uvmap and compat.check_version(2, 80, 0) < 0:
        for mtrl_idx, face_indices in mtrl_map.items():
            tex_layer = new_mesh.uv_textures[0]
            for face_idx in face_indices:
                tex_layer.data[face_idx].image = materials[mtrl_idx]["image"]

    # add mirror modifier
    if mqo_obj.mirror is not None:
        if MQO_TO_BLENDER_MIRROR_TYPE[mqo_obj.mirror] != 'NONE':
            bpy.ops.object.modifier_add(type='MIRROR')
            axis_index = mqo_obj.mirror_axis
            if compat.check_version(2, 80, 0) >= 0:
                for i in new_obj.modifiers["Mirror"].use_axis:
                    new_obj.modifiers["Mirror"].use_axis[i] = False
                if axis_index & 0x1:
                    new_obj.modifiers["Mirror"].use_axis[0] = True
                if axis_index & 0x2:
                    new_obj.modifiers["Mirror"].use_axis[1] = True
                if axis_index & 0x4:
                    new_obj.modifiers["Mirror"].use_axis[2] = True
            else:
                new_obj.modifiers["Mirror"].use_x = False
                new_obj.modifiers["Mirror"].use_y = False
                new_obj.modifiers["Mirror"].use_z = False
                if axis_index & 0x1:
                    new_obj.modifiers["Mirror"].use_x = True
                if axis_index & 0x2:
                    new_obj.modifiers["Mirror"].use_y = True
                if axis_index & 0x4:
                    new_obj.modifiers["Mirror"].use_z = True

    new_obj.delta_rotation_euler = (math.radians(90), 0, 0)
    new_obj.delta_scale = (0.01, 0.01, 0.01)

    return new_obj


def import_objects(mqo_file, exclude_objects, materials,
                   vertex_weight_import_options):
    objects_imported = []
    for mqo_obj in mqo_file.get_objects():
        if mqo_obj.name in exclude_objects:
            continue
        objects_imported.append(
            import_object(mqo_obj, materials, vertex_weight_import_options))

    return objects_imported


def import_mqo_file(filepath, exclude_objects, exclude_materials,
                    import_prefix, vertex_weight_import_options):
    mqo_file = mqo.MqoFile()
    mqo_file.load(filepath)

    orig_mode = compat.get_object_mode(bpy.context)
    if bpy.ops.object.mode_set.poll() and orig_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    materials_imported = import_materials(mqo_file, filepath,
                                          exclude_materials)
    objects_imported = import_objects(mqo_file, exclude_objects,
                                      materials_imported,
                                      vertex_weight_import_options)

    # set import prefix
    for mtrl in materials_imported:
        if mtrl["material"] is None:
            continue
        mtrl["material"].name = "{}{}".format(
            import_prefix, mtrl["material"].name)
    for obj in objects_imported:
        obj.name = "{}{}".format(import_prefix, obj.name)

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode=orig_mode)


def export_material_v279(mqo_file, material):
    mqo_mtrl = mqo.Material()
    mqo_mtrl.name = material.name
    mqo_mtrl.color = [*material.diffuse_color[0:3], 1.0]
    mqo_mtrl.diffuse = material.diffuse_intensity
    mqo_mtrl.specular = material.specular_intensity
    mqo_mtrl.emissive = material.emit
    mqo_mtrl.ambient = material.ambient
    mqo_file.add_material(mqo_mtrl)


def export_material_v280(mqo_file, material):
    if not material.use_nodes:
        return

    mqo_mtrl = mqo.Material()
    mqo_mtrl.name = material.name
    output_node = next(n for n in material.node_tree.nodes
                       if n.type == "OUTPUT_MATERIAL")

    links = output_node.inputs['Surface'].links
    if len(links) != 1:
        return

    material_node = links[0].from_node
    if material_node.type == 'EEVEE_SPECULAR':
        mqo_mtrl.color = material_node.inputs["Base Color"].default_value
        mqo_mtrl.specular = material_node.inputs["Specular"].default_value[0]
        mqo_mtrl.emissive =\
            material_node.inputs["Emissive Color"].default_value[0]
    elif material_node.type == 'BSDF_PRINCIPLED':
        mqo_mtrl.color = material_node.inputs["Base Color"].default_value
        mqo_mtrl.specular =\
            material_node.inputs["Specular Tint"].default_value[0]
        mqo_mtrl.emissive =\
            material_node.inputs["Emission Color"].default_value[0]
    elif material_node.type == 'TEX_IMAGE':
        mqo_mtrl.texture_map = bpy.path.basename(material_node.image.filepath)
        mqo_mtrl.projection_type = BLENDER_TO_MQO_PROJECTION_TYPE[
            material_node.projection]
    else:
        return

    mqo_file.add_material(mqo_mtrl)


def export_material(mqo_file, material):
    if compat.check_version(2, 80, 0) >= 0:
        return export_material_v280(mqo_file, material)

    return export_material_v279(mqo_file, material)


def export_materials(mqo_file, exclude_materials):
    for mtrl in bpy.data.materials:
        if mtrl.name in exclude_materials:
            continue
        export_material(mqo_file, mtrl)


# pylint: disable=unused-argument
def attach_texture_to_material_v280(mqo_file, exclude_objects,
                                    exclude_materials, export_objects):
    pass


def attach_texture_to_material_v279(mqo_file, exclude_objects,
                                    exclude_materials, export_objects):
    # objects
    for obj in export_objects:
        if obj.name in exclude_objects:
            continue

        # object mode -> edit mode
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='EDIT')

        # materials
        for mtrl_idx, mtrl_slot in enumerate(obj.material_slots):
            if mtrl_slot.material.name in exclude_materials:
                continue   # does not export material index

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            mtrl = mtrl_slot.material
            obj.active_material_index = mtrl_idx
            obj.active_material = mtrl
            bpy.ops.object.material_slot_select()

            # Mode switch is required to reflect the selection result of
            # bpy.ops.object.material_slot_select()
            bpy.ops.object.mode_set(mode='OBJECT')

            # find material index for mqo
            for i, mqo_mtrl in enumerate(mqo_file.get_materials()):
                if mtrl.name == mqo_mtrl.name:
                    mqo_mtrl_idx = i
                    break
            else:
                continue

            me = obj.data
            tex_layer = me.uv_textures.active
            if not me.uv_textures.items():
                continue
            for face in me.polygons:
                if face.select and face.index < len(tex_layer.data):
                    image_face = face
                    break
            else:
                continue

            # attch texture to material
            texture_path = bpy.path.basename(
                tex_layer.data[image_face.index].image.filepath)
            mqo_file.get_materials()[mqo_mtrl_idx].texture_map = texture_path

        # edit mode -> object mode
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')


def attach_texture_to_material(mqo_file, exclude_objects, exclude_materials,
                               export_objects):
    if compat.check_version(2, 80, 0) >= 0:
        attach_texture_to_material_v280(
            mqo_file, exclude_objects, exclude_materials, export_objects)
    else:
        attach_texture_to_material_v279(
            mqo_file, exclude_objects, exclude_materials, export_objects)


def export_mqo_file(filepath, exclude_objects, exclude_materials,
                    export_prefix, vertex_weight_export_options):
    mqo_file = mqo.MqoFile()
    mqo_file.version = "1.1"
    mqo_file.format = "Text"

    scene = mqo.Scene()
    scene.set_default_params()
    mqo_file.scene = scene

    export_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    orig_mode = compat.get_object_mode(bpy.context)
    if bpy.ops.object.mode_set.poll() and orig_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # materials
    export_materials(mqo_file, exclude_materials)

    # attach texture on materials
    attach_texture_to_material(mqo_file, exclude_objects, exclude_materials,
                               export_objects)

    # objects
    for obj in export_objects:
        if obj.name in exclude_objects:
            continue

        # copy object
        copied_obj = obj.copy()
        copied_obj.data = obj.data.copy()
        if compat.check_version(2, 80, 0) >= 0:
            bpy.context.scene.collection.objects.link(copied_obj)
            bpy.context.view_layer.objects.active = copied_obj
            copied_obj.select_set(True)
        else:
            bpy.context.scene.objects.link(copied_obj)
            bpy.context.scene.objects.active = copied_obj
            copied_obj.select = True

        # apply all modifiers
        for mod in copied_obj.modifiers:
            bpy.ops.object.modifier_apply(modifier=mod.name)

        if bpy.ops.object.mode_set.poll():
            # uv_layer.data requires object mode.
            bpy.ops.object.mode_set(mode='OBJECT')

        mqo_obj = mqo.Object()
        mqo_obj.name = obj.name

        me = copied_obj.data

        # vertices
        for v in me.vertices:
            mqo_obj.add_vertex([v.co[0], v.co[1], v.co[2]])

        # faces
        for face in me.polygons:
            mqo_face = mqo.Face()
            mqo_face.ngons = len(face.vertices)
            mqo_face.vertex_indices = [v for v in face.vertices]    # pylint: disable=R1721 # noqa
            if len(me.uv_layers.keys()) > 0:
                uv_layer = me.uv_layers.active
                for li in list(face.loop_indices):
                    if li >= len(uv_layer.data):
                        continue
                    uv = uv_layer.data[li].uv
                    if mqo_face.uv_coords is None:
                        mqo_face.uv_coords = []
                    mqo_face.uv_coords.append([uv[0], 1 - uv[1]])
            mqo_obj.add_face(mqo_face)

        bpy.ops.object.editmode_toggle()    # object mode -> edit mode

        # Changing mesh select mode is required to reflect the material
        # assignments.
        mesh_select_mode_orig = list(
            bpy.context.tool_settings.mesh_select_mode)
        bpy.context.tool_settings.mesh_select_mode = (False, False, True)

        # materials
        for mtrl_idx, mtrl_slot in enumerate(copied_obj.material_slots):
            if mtrl_slot.material.name in exclude_materials:
                continue   # does not export material index

            bpy.ops.mesh.select_all(action='DESELECT')
            mtrl = mtrl_slot.material
            copied_obj.active_material_index = mtrl_idx
            copied_obj.active_material = mtrl
            bpy.ops.object.material_slot_select()

            # Mode switch is required to reflect the selection result of
            # bpy.ops.object.material_slot_select()
            bpy.ops.object.editmode_toggle()    # edit mode -> object mode
            bpy.ops.object.editmode_toggle()    # object mode -> edit mode

            # find material index for mqo
            mqo_mtrl_idx = -1
            for i, mqo_mtrl in enumerate(mqo_file.get_materials()):
                if mtrl.name == mqo_mtrl.name:
                    mqo_mtrl_idx = i
                    break
            # set material index
            for bl_face, mqo_face in zip(me.polygons, mqo_obj.get_faces()):
                if bl_face.select:
                    mqo_face.material = mqo_mtrl_idx

        bpy.context.tool_settings.mesh_select_mode = mesh_select_mode_orig

        # Vertex weights.
        if vertex_weight_export_options.export:
            vertex_groups = \
                vertex_weight_export_options.target_groups[obj.name]

            mqo_vertex_attr = mqo.Object.VertexAttr()
            has_vertex_attr = False
            for vg in obj.vertex_groups:
                if vg.name not in vertex_groups:
                    continue
                for v in me.vertices:
                    try:
                        mqo_vertex_attr.weit[v.index] = vg.weight(v.index)
                        has_vertex_attr = True
                    except RuntimeError:
                        # This error will be raised when the vertex is not in
                        # the group.
                        pass

            if has_vertex_attr:
                mqo_obj.merge_vertexattr(mqo_vertex_attr)

        # edit mode -> object mode
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        mqo_file.add_object(mqo_obj)

        if compat.check_version(2, 80, 0) >= 0:
            bpy.context.scene.collection.objects.unlink(copied_obj)
        else:
            bpy.context.scene.objects.unlink(copied_obj)
        bpy.data.objects.remove(copied_obj)

    # set export prefix
    for mqo_obj in mqo_file.get_objects():
        mqo_obj.name = "{}{}".format(export_prefix, mqo_obj.name)
    for mqo_mtrl in mqo_file.get_materials():
        mqo_mtrl.name = "{}{}".format(export_prefix, mqo_mtrl.name)

    mqo_file.save(filepath)
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode=orig_mode)


class VertexWeightImportOptions():
    def __init__(self, import_=True, grouped_by='ALL_IN_ONE',
                 group_name="Vertex Weights Group"):
        self.import_ = import_
        self.grouped_by = grouped_by
        self.group_name = group_name


@compat.make_annotations
class BLMQO_ObjectImportPropertyCollection(bpy.types.PropertyGroup):
    object_name = StringProperty(name="Object Name", default="")
    valid = BoolProperty(name="Valid", default=False)
    import_ = BoolProperty(name="", default=True)


@compat.make_annotations
class BLMQO_MaterialImportPropertyCollection(bpy.types.PropertyGroup):
    material_name = StringProperty(name="Material Name", default="")
    valid = BoolProperty(name="Valid", default=False)
    import_ = BoolProperty(name="", default=True)


@BlClassRegistry()
@compat.make_annotations
class BLMQO_OT_ImportMqo(bpy.types.Operator, ImportHelper):

    bl_idname = "import_scene.blmqo_ot_import_mqo"
    bl_label = "Import Metasequoia file (.mqo)"
    bl_description = "Import a Metasequoia file"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".mqo"
    filter_glob = StringProperty(default="*.mqo;*.mqoz")

    import_objects = BoolProperty(name="Import Objects", default=True)
    objects_to_import = bpy.props.CollectionProperty(
        name="Objects to Import",
        type=BLMQO_ObjectImportPropertyCollection
    )
    import_materials = BoolProperty(name="Import Materials", default=True)
    materials_to_import = bpy.props.CollectionProperty(
        name="Materials to Import",
        type=BLMQO_MaterialImportPropertyCollection
    )
    import_vertex_weights = BoolProperty(
        name="Import Vertex Weights",
        default=True,
    )
    vertex_weights_grouped_by = EnumProperty(
        name="Grouped by",
        description="How to group vertex weights",
        items=[
            ('ALL_IN_ONE', "All In One",
             "Vertex weights are grouped as a single vertex group"),
            ('WEIGHT_VALUE', "Weight Value",
             "Vertex weights are grouped as multiple vertex groups that has "
             "a same weight value.")
        ],
        default='ALL_IN_ONE'
    )
    vertex_weights_group_name = StringProperty(
        name="Group Name",
        default="Vertex Weights Group"
    )
    add_import_prefix = BoolProperty(
        name="Add Import Prefix to Asset Names",
        default=True
    )
    import_prefix = StringProperty(name="Prefix", default="[Imported] ")

    prev_selected_file = ""
    is_valid_mqo_file = False
    invalid_mqo_file_reason = ""
    num_valid_objects = 0
    num_valid_materials = 0

    def draw(self, context):
        layout = self.layout
        user_prefs = compat.get_user_preferences(context)
        if user_prefs is None:
            return
        prefs = user_prefs.addons[__package__].preferences

        if (prefs.selective_import
                and self.prev_selected_file != self.properties.filepath):
            self.num_valid_objects = 0
            self.num_valid_materials = 0
            mqo_file = mqo.MqoFile()
            try:
                mqo_file.load(self.properties.filepath)
                self.is_valid_mqo_file = True
            except:     # noqa
                self.is_valid_mqo_file = False
                self.invalid_mqo_file_reason = "Not MQO file."

            if self.is_valid_mqo_file:
                if len(mqo_file.get_objects()) > \
                        prefs.importable_objects_limit:
                    self.is_valid_mqo_file = False
                    self.invalid_mqo_file_reason = \
                        "Importable objects limit exceeded."
                if len(mqo_file.get_materials()) > \
                        prefs.importable_materials_limit:
                    self.is_valid_mqo_file = False
                    self.invalid_mqo_file_reason = \
                        "Importable materials limit exceeded."

            if self.is_valid_mqo_file:
                for oi in self.objects_to_import:
                    oi.valid = False
                    oi.object_name = ""
                    oi.import_ = True
                for i, obj in enumerate(mqo_file.get_objects()):
                    self.objects_to_import[i].valid = True
                    self.objects_to_import[i].object_name = obj.name
                    self.objects_to_import[i].import_ = True
                    self.num_valid_objects += 1

                for mi in self.materials_to_import:
                    mi.valid = False
                    mi.object_name = ""
                    mi.import_ = True
                for i, mtrl in enumerate(mqo_file.get_materials()):
                    self.materials_to_import[i].valid = True
                    self.materials_to_import[i].material_name = mtrl.name
                    self.materials_to_import[i].import_ = True
                    self.num_valid_materials += 1

                self.is_valid_mqo_file = True
                self.invalid_mqo_file_reason = ""

            self.prev_selected_file = self.properties.filepath

        if prefs.selective_import and not self.is_valid_mqo_file:
            layout.label(text=self.invalid_mqo_file_reason)
            return

        layout.label(text="File: {}".format(self.properties.filepath))

        layout.prop(self, "import_objects")
        if (prefs.selective_import
                and self.import_objects
                and self.num_valid_objects > 0):
            sp = compat.layout_split(layout, factor=0.01)
            sp.column()     # Spacer.
            sp = compat.layout_split(sp, factor=1.0)
            col = sp.column()
            box = col.box()
            for oi in self.objects_to_import:
                if oi.valid:
                    box.prop(oi, "import_", text=oi.object_name)

        layout.prop(self, "import_materials")
        if (prefs.selective_import
                and self.import_materials
                and self.num_valid_materials > 0):
            sp = compat.layout_split(layout, factor=0.01)
            sp.column()     # Spacer.
            sp = compat.layout_split(sp, factor=1.0)
            col = sp.column()
            box = col.box()
            for mi in self.materials_to_import:
                if mi.valid:
                    box.prop(mi, "import_", text=mi.material_name)

        layout.prop(self, "import_vertex_weights")
        if self.import_vertex_weights:
            layout.prop(self, "vertex_weights_grouped_by")
            layout.prop(self, "vertex_weights_group_name")
        layout.prop(self, "add_import_prefix")
        if self.add_import_prefix:
            layout.prop(self, "import_prefix")

    def execute(self, context):
        if not self.properties.filepath:
            raise ValueError("Filepath is not set")

        user_prefs = compat.get_user_preferences(context)
        prefs = user_prefs.addons[__package__].preferences

        if prefs.selective_import and not self.is_valid_mqo_file:
            self.report(
                {'WARNING'},
                "{} (file: {})"
                .format(self.invalid_mqo_file_reason,
                        self.properties.filepath))
            return {'CANCELLED'}

        exclude_objects = [
            oi.object_name
            for oi in self.objects_to_import
            if oi.valid and not oi.import_
        ]
        exclude_materials = [
            mi.material_name
            for mi in self.materials_to_import
            if mi.valid and not mi.import_
        ]
        vertex_weight_import_options = VertexWeightImportOptions(
            self.import_vertex_weights,
            self.vertex_weights_grouped_by,
            self.vertex_weights_group_name
        )
        import_mqo_file(self.properties.filepath,
                        exclude_objects, exclude_materials,
                        self.import_prefix if self.add_import_prefix else "",
                        vertex_weight_import_options)

        self.report({'INFO'},
                    "Imported from {}".format(self.properties.filepath))

        return {'FINISHED'}

    def invoke(self, context, _):
        wm = context.window_manager
        user_prefs = compat.get_user_preferences(context)
        prefs = user_prefs.addons[__package__].preferences

        self.objects_to_import.clear()
        self.materials_to_import.clear()
        if prefs.selective_import:
            for _ in range(prefs.importable_objects_limit):

                # Add properties for object.
                item = self.objects_to_import.add()
                item.object_name = ""
                item.valid = False
                item.import_ = True

            for _ in range(prefs.importable_materials_limit):
                # Add properties for materials.
                item = self.materials_to_import.add()
                item.material_name = ""
                item.valid = False
                item.import_ = True

        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}


class VertexWeightExportOptions():
    def __init__(self, export, target_groups):
        self.export = export
        self.target_groups = target_groups      # { object: vertex_group }


@compat.make_annotations
class BLMQO_ObjectExportPropertyCollection(bpy.types.PropertyGroup):
    object_name = StringProperty(name="Object Name", default="")
    export_ = BoolProperty(name="", default=True)


@compat.make_annotations
class BLMQO_MaterialExportPropertyCollection(bpy.types.PropertyGroup):
    material_name = StringProperty(name="Material Name", default="")
    export_ = BoolProperty(name="", default=True)


@compat.make_annotations
class BLMQO_VertexWeightExportPropertyCollection(bpy.types.PropertyGroup):
    object_name = StringProperty(name="Object Name", default="")
    vertex_group_name = StringProperty(name="Vertex Group Name", default="")
    export_ = BoolProperty(name="", default=True)


@BlClassRegistry()
@compat.make_annotations
class BLMQO_OT_ExportMqo(bpy.types.Operator, ExportHelper):

    bl_idname = "export_scene.blmqo_ot_export_mqo"
    bl_label = "Export Metasequoia file (.mqo)"
    bl_description = "Export a Metasequoia file"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".mqo"
    filter_glob = StringProperty(default="*.mqo", options={'HIDDEN'})

    def get_objects_for_vertex_weights(self, context):
        # TODO: select only objects to export.
        items = []
        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue
            items.append((obj.name, obj.name, obj.name))
        return items

    export_mode = EnumProperty(
        name="Export Mode",
        description="Export Mode",
        items=[
            ('SELECTED_OBJECT', "Selected Objects", "Export selected objects"),
            ('MANUAL', "Manual", "Export manually selected assets"),
        ],
        default='SELECTED_OBJECT',
    )

    export_objects = BoolProperty(name="Export Objects", default=True)
    objects_to_export = bpy.props.CollectionProperty(
        name="Objects to Export",
        type=BLMQO_ObjectExportPropertyCollection
    )
    export_materials = BoolProperty(name="Export Materials", default=True)
    materials_to_export = bpy.props.CollectionProperty(
        name="Materials to Export",
        type=BLMQO_MaterialExportPropertyCollection
    )
    export_vertex_weights = BoolProperty(
        name="Export Vertex Weights",
        default=True,
    )
    vertex_weights_to_export = bpy.props.CollectionProperty(
        name="Vertex Weights to Export",
        type=BLMQO_VertexWeightExportPropertyCollection
    )
    objects_for_vertex_weights = EnumProperty(
        name="Object",
        items=get_objects_for_vertex_weights,
    )
    add_export_prefix = BoolProperty(
        name="Add Export Prefix to Asset Names",
        default=True
    )
    export_prefix = StringProperty(name="Prefix", default="[Exported] ")

    def draw(self, _):
        layout = self.layout

        layout.prop(self, "export_mode")

        if self.export_mode == 'SELECTED_OBJECT':
            layout.prop(self, "export_materials")
            layout.prop(self, "export_vertex_weights")
        elif self.export_mode == 'MANUAL':
            object_to_vertex_groups = {}
            for vg_idx, _ in enumerate(self.vertex_weights_to_export):
                vg = self.vertex_weights_to_export[vg_idx]
                if vg.object_name not in object_to_vertex_groups:
                    object_to_vertex_groups[vg.object_name] = []
                object_to_vertex_groups[vg.object_name].append(vg)

            layout.prop(self, "export_objects")
            if self.export_objects and len(self.objects_to_export) > 0:
                sp = compat.layout_split(layout, factor=0.01)
                sp.column()     # Spacer.
                sp = compat.layout_split(sp, factor=1.0)
                col = sp.column()
                box = col.box()
                for oe in self.objects_to_export:
                    box.prop(oe, "export_", text=oe["object_name"])

            layout.prop(self, "export_materials")
            if self.export_materials and len(self.materials_to_export) > 0:
                sp = compat.layout_split(layout, factor=0.01)
                sp.column()     # Spacer.
                sp = compat.layout_split(sp, factor=1.0)
                col = sp.column()
                box = col.box()
                for me in self.materials_to_export:
                    box.prop(me, "export_", text=me["material_name"])

            layout.prop(self, "export_vertex_weights")
            if self.export_vertex_weights:
                layout.prop(self, "objects_for_vertex_weights")
                sp = compat.layout_split(layout, factor=0.01)
                sp.column()
                sp = compat.layout_split(sp, factor=1.0)
                col = sp.column()   # Spacer.
                for obj_name, vertex_groups in object_to_vertex_groups.items():
                    if obj_name != self.objects_for_vertex_weights:
                        continue
                    box = col.box()
                    for group in vertex_groups:
                        box.prop(group, "export_",
                                 text=group.vertex_group_name)

        layout.prop(self, "add_export_prefix")
        if self.add_export_prefix:
            layout.prop(self, "export_prefix")

    def execute(self, _):
        if not self.properties.filepath:
            raise ValueError("Filepath is not set")

        exclude_objects = set()
        exclude_materials = set()
        vertex_groups = {}

        if self.export_mode == 'SELECTED_OBJECT':
            exclude_objects = {
                o.name
                for o in bpy.data.objects
                if not compat.get_object_select(o)
            }

            used_materials = set()
            for obj in bpy.data.objects:
                if obj.name in exclude_objects:
                    continue
                for mtrl_slot in obj.material_slots:
                    used_materials.add(mtrl_slot.material.name)
            all_materials = {m.name for m in bpy.data.materials}
            exclude_materials = all_materials - used_materials
        elif self.export_mode == 'MANUAL':
            exclude_objects = {
                oe.object_name
                for oe in self.objects_to_export
                if not oe.export_
            }
            exclude_materials = {
                me.material_name
                for me in self.materials_to_export
                if not me.export_
            }

        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue
            vertex_groups[obj.name] = []    # TODO: Use export object property.
        for vg_idx, _ in enumerate(self.vertex_weights_to_export):
            vg = self.vertex_weights_to_export[vg_idx]
            if vg.export_:
                vertex_groups[vg.object_name].append(vg.vertex_group_name)

        vertex_weight_export_options = VertexWeightExportOptions(
            self.export_vertex_weights, vertex_groups
        )
        export_mqo_file(self.properties.filepath, exclude_objects,
                        exclude_materials,
                        self.export_prefix if self.add_export_prefix else "",
                        vertex_weight_export_options)

        self.report({'INFO'},
                    "Exported to {}".format(self.properties.filepath))

        return {'FINISHED'}

    def invoke(self, context, event):
        self.properties.filepath = "untitled.mqo"

        wm = context.window_manager

        self.objects_to_export.clear()
        self.vertex_weights_to_export.clear()
        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue

            # Add properties for object.
            item = self.objects_to_export.add()
            item.object_name = obj.name
            item.export_ = True

            # Add proeprties for vertex weight.
            for vg in obj.vertex_groups:
                item = self.vertex_weights_to_export.add()
                item.object_name = obj.name
                item.vertex_group_name = vg.name
                item.export_ = True

        self.materials_to_export.clear()
        for mtrl in bpy.data.materials:
            item = self.materials_to_export.add()
            item.material_name = mtrl.name
            item.export_ = True

        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}


def topbar_mt_file_import_fn(self, _):
    layout = self.layout

    layout.operator(BLMQO_OT_ImportMqo.bl_idname,
                    text="Metasequoia (.mqo)")


def topbar_mt_file_export_fn(self, _):
    layout = self.layout

    layout.operator(BLMQO_OT_ExportMqo.bl_idname,
                    text="Metasequoia (.mqo)")
