import sys
import unittest
import math

import bpy
import bmesh


TESTEE_FILE = "testee.blend"
ALLOWABLE_ERROR = 1e-2


def check_version(major, minor, _):
    """
    Check blender version
    """

    if bpy.app.version[0] == major and bpy.app.version[1] == minor:
        return 0
    if bpy.app.version[0] > major:
        return 1
    if bpy.app.version[0] < major:
        return -1
    if bpy.app.version[1] > minor:
        return 1
    return -1


def memorize_view_3d_mode(fn):
    def __memorize_view_3d_mode(*args, **kwargs):
        orig_mode = bpy.context.mode
        result = fn(*args, **kwargs)
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode=orig_mode)
        return result
    return __memorize_view_3d_mode


@memorize_view_3d_mode
def get_num_vertices(obj):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(obj.data)
    num_verts = len(bm.verts)
    return num_verts


@memorize_view_3d_mode
def get_num_faces(obj):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(obj.data)
    num_faces = len(bm.faces)
    return num_faces


def is_float_same(f0, f1):
    return math.fabs(f0 - f1) < ALLOWABLE_ERROR


def is_v2_same(v0, v1):
    if is_float_same(v0[0], v1[0]) and \
       is_float_same(v0[1], v1[1]):
        return True
    return False


def is_v3_same(v0, v1):
    if is_float_same(v0[0], v1[0]) and \
       is_float_same(v0[1], v1[1]) and \
       is_float_same(v0[2], v1[2]):
        return True
    return False


def is_same(var1, var2, allowable_erorr=ALLOWABLE_ERROR):
    # pylint: disable=R1705,R0911
    if (var1 is None) and (var2 is None):
        return True
    elif type(var1) != type(var2):  # pylint: disable=unidiomatic-typecheck
        return False
    elif isinstance(var1, int) and isinstance(var2, int):
        if var1 != var2:
            return False
    elif isinstance(var1, float) and isinstance(var2, float):
        if math.fabs(var1 - var2) > allowable_erorr:
            return False
    elif isinstance(var1, str) and isinstance(var2, str):
        if var1 != var2:
            return False
    elif isinstance(var1, list) and isinstance(var2, list):
        for elm1, elm2 in zip(var1, var2):
            if not is_same(elm1, elm2):
                return False
    else:
        raise RuntimeError("Not supported type (var1: {}, var2: {})"
                           .format(type(var1), type(var2)))
    return True


@memorize_view_3d_mode
def valid_vertices(bl_obj, mqo_obj):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(bl_obj.data)
    for bl_vert, mqo_vert in zip(bm.verts, mqo_obj.get_vertices()):
        if not is_v3_same(bl_vert.co, mqo_vert):
            print("Vertex coords do not match {} vs {}"
                  .format(bl_vert.co, mqo_vert))
            return False
    return True


def is_same_face(mqo_obj, bl_face, mqo_face):
    for bl_vert, mqo_vert in zip(bl_face.verts, mqo_face.vertex_indices):
        if bl_vert.index != mqo_vert:
            print("Vertex index does not match {} vs {}"
                  .format(bl_vert.index, mqo_vert))
            return False
        mqo_vert_co = mqo_obj.get_vertices()[mqo_vert]
        if not is_v3_same(bl_vert.co, mqo_vert_co):
            print("Vertex coords do not match {} vs {}"
                  .format(bl_vert.co, mqo_vert_co))
            return False
    return True


@memorize_view_3d_mode
def valid_faces(bl_obj, mqo_obj):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(bl_obj.data)
    for bl_face, mqo_face in zip(bm.faces, mqo_obj.get_faces(uniq=True)):
        if not is_same_face(mqo_obj, bl_face, mqo_face):
            return False

    return True


@memorize_view_3d_mode
def valid_material_assignment(bl_obj, mqo_obj, bl_mtrl, mqo_mtrl_index):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')

    bl_mtrl_index = [i
                     for i, m in enumerate(bl_obj.material_slots[:])
                     if m.name == bl_mtrl.name][0]
    bl_obj.active_material_index = bl_mtrl_index
    bm = bmesh.from_edit_mesh(bl_obj.data)
    for face in bm.faces:
        face.select = False
    bpy.ops.object.material_slot_select()
    selected_faces = []
    for face in bm.faces:
        if face.select:
            selected_faces.append(face.index)
    for bl_face, mqo_face in zip(bm.faces, mqo_obj.get_faces(uniq=True)):
        if not is_same_face(mqo_obj, bl_face, mqo_face):
            return False

        if bl_face.select:
            if mqo_face.material != mqo_mtrl_index:
                print("Material '{}' index does not match {} vs {}"
                      .format(bl_mtrl.name, mqo_face.material, mqo_mtrl_index))
                return False

    return True


@memorize_view_3d_mode
def valid_uvs(bl_obj, mqo_obj):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(bl_obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    for bl_face, mqo_face in zip(bm.faces, mqo_obj.get_faces(uniq=True)):
        bl_uvs = [[lo[uv_layer].uv[0], lo[uv_layer].uv[1]]
                  for lo in bl_face.loops]
        for bl_uv, mqo_uv in zip(bl_uvs, mqo_face.uv_coords):
            # Metasequoia V-coordinate need to be inverted for meeting
            # Blender V-coordinate.
            mqo_uv_corrected = mqo_uv.copy()
            mqo_uv_corrected[1] = 1 - mqo_uv_corrected[1]
            if not is_v2_same(bl_uv, mqo_uv_corrected):
                print("UV coords do not match {} vs {}".format(
                    bl_uv, mqo_uv_corrected))
                return False

    return True


def valid_mirror_modifier(bl_mod, mqo_obj):
    # pylint: disable=R0911
    if check_version(2, 80, 0) >= 0:
        axis_index = mqo_obj.mirror_axis
        if axis_index & 0x1:
            if not bl_mod.use_axis[0]:
                return False
        if axis_index & 0x2:
            if not bl_mod.use_axis[1]:
                return False
        if axis_index & 0x4:
            if not bl_mod.use_axis[2]:
                return False
    else:
        axis_index = mqo_obj.mirror_axis
        if axis_index & 0x1:
            if not bl_mod.use_x:
                return False
        if axis_index & 0x2:
            if not bl_mod.use_y:
                return False
        if axis_index & 0x4:
            if not bl_mod.use_z:
                return False

    return True


@memorize_view_3d_mode
def valid_vertexattr(bl_obj, mqo_obj):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(bl_obj.data)
    bl_weights = {}
    for vg in bl_obj.vertex_groups:
        for v in bm.verts:
            try:
                w = vg.weight(v.index)
                bl_weights[v.index] = w
            except RuntimeError:
                pass

    mqo_weights = mqo_obj.get_vertexattr('WEIT')
    if mqo_weights is None:
        mqo_weights = {}

    if len(bl_weights.keys()) != len(mqo_weights.keys()):
        print("Number of vertexattr 'WEIT' does not match {} vs {}"
              .format(len(bl_weights.keys()), len(mqo_weights.keys())))
        return False

    for vidx, bl_w in bl_weights.items():
        mqo_w = mqo_weights[vidx]
        if not is_float_same(bl_w, mqo_w):
            print("Vertexattr 'WEIT' value does not match {} vs {}"
                  .format(bl_w, mqo_w))
            return False

    return True


def select_object_only(obj_name):
    for o in bpy.data.objects:
        if o.name == obj_name:
            if check_version(2, 80, 0) >= 0:
                o.select_set(True)
            else:
                o.select = True
        else:
            if check_version(2, 80, 0) >= 0:
                o.select_set(False)
            else:
                o.select = False


def check_addon_enabled(mod):
    if check_version(2, 80, 0) >= 0:
        result = bpy.ops.preferences.addon_enable(module=mod)
    else:
        result = bpy.ops.wm.addon_enable(module=mod)
    assert (result == {'FINISHED'}), "Failed to enable add-on {}".format(mod)
    if check_version(2, 80, 0) >= 0:
        assert mod in bpy.context.preferences.addons.keys(),\
               "Failed to enable add-on {}".format(mod)
    else:
        assert mod in bpy.context.user_preferences.addons.keys(),\
               "Failed to enable add-on {}".format(mod)


def check_addon_disabled(mod):
    if check_version(2, 80, 0) >= 0:
        result = bpy.ops.preferences.addon_disable(module=mod)
    else:
        result = bpy.ops.wm.addon_disable(module=mod)
    assert (result == {'FINISHED'}), "Failed to disable add-on {}".format(mod)
    if check_version(2, 80, 0) >= 0:
        assert mod not in bpy.context.preferences.addons.keys(),\
               "Failed to disable add-on {}".format(mod)
    else:
        assert mod not in bpy.context.user_preferences.addons.keys(),\
               "Failed to disable add-on {}".format(mod)


def operator_exists(idname):
    try:
        from bpy.ops import op_as_string    # pylint: disable=C0415
        op_as_string(idname)
        return True
    except:     # noqa
        try:
            from bpy.ops import _op_as_string   # pylint: disable=C0415
            _op_as_string(idname)
            return True
        except:     # pylint: disable=W0702 # noqa
            return False


def menu_exists(idname):
    return idname in dir(bpy.types)


class TestBase(unittest.TestCase):

    package_name = "blender_mqo"
    module_name = ""
    submodule_name = None
    idname = []

    @classmethod
    def setUpClass(cls):
        if check_version(4, 2, 0) >= 0:
            cls.package_name = "bl_ext.user_default." + cls.package_name

        if cls.submodule_name is not None:
            print("\n======== Module Test: {}.{} ({}) ========"
                  .format(cls.package_name, cls.module_name,
                          cls.submodule_name))
        else:
            print("\n======== Module Test: {}.{} ========"
                  .format(cls.package_name, cls.module_name))
        try:
            # create empty .blend file
            bpy.ops.wm.read_factory_settings()
            for o in bpy.data.objects:
                if check_version(2, 80, 0) >= 0:
                    o.select_set(True)
                else:
                    o.select = True
            bpy.ops.object.delete()
            for i in bpy.data.images.values():
                bpy.data.images.remove(i)
            for i in bpy.data.materials.values():
                bpy.data.materials.remove(i)
            for i in bpy.data.textures.values():
                bpy.data.textures.remove(i)

            # check if all add-on's operators are enabled
            check_addon_enabled(cls.package_name)
            for op in cls.idname:
                if op[0] == 'OPERATOR':
                    assert operator_exists(op[1]), \
                        "Operator {} does not exist".format(op[1])
                elif op[0] == 'MENU':
                    assert menu_exists(op[1]), \
                        "Menu {} does not exist".format(op[1])

            # save .blend file
            bpy.ops.wm.save_as_mainfile(filepath=TESTEE_FILE)
        except AssertionError as e:
            print(e)
            sys.exit(1)

    @classmethod
    def tearDownClass(cls):
        try:
            # check if all add-on's operators are disabled
            check_addon_disabled(cls.package_name)
            for op in cls.idname:
                if op[0] == 'OPERATOR':
                    assert not operator_exists(op[1]),\
                           "Operator {} exists".format(op[1])
                elif op[0] == 'MENU':
                    assert not menu_exists(op[1]),\
                           "Menu {} exists".format(op[1])
        except AssertionError as e:
            print(e)
            sys.exit(1)

    def setUp(self):
        bpy.ops.wm.open_mainfile(filepath=TESTEE_FILE)
        self.setUpEachMethod()

    # pylint: disable=C0103
    def setUpEachMethod(self):
        pass

    def tearDown(self):
        pass
