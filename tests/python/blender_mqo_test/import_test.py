import os

import bpy

try:
    from blender_mqo.utils.mqo_file import MqoFile
except:     # pylint: disable=W0702 # noqa
    from bl_ext.user_default.blender_mqo.utils.mqo_file import MqoFile
from . import common


MQO_FILE_DIR = "mqo_files"


class TestImportMqo(common.TestBase):
    module_name = "import_scene"
    idname = [
        ('OPERATOR', 'import_scene.blmqo_ot_import_mqo')
    ]

    def setUpEachMethod(self):
        pass

    def test_import_mqo_simple(self):
        filepath = "{}/{}/simple.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath)

        self.assertEqual(len(bpy.data.objects), 0,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 0,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

    def test_import_mqo_only_scene(self):
        filepath = "{}/{}/scene.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath)

        self.assertEqual(len(bpy.data.objects), 0,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 0,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

    def test_import_mqo_with_thumnail(self):
        filepath = "{}/{}/thumbnail.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath)

        self.assertEqual(len(bpy.data.objects), 0,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 0,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

    def _valid_object(self, mqo_file, obj_name, expect_num_vert,
                      expect_num_face):
        common.select_object_only(obj_name)
        bl_obj = bpy.data.objects[obj_name]
        if common.check_version(2, 80, 0) >= 0:
            bpy.context.view_layer.objects.active = bl_obj
        else:
            bpy.context.scene.objects.active = bl_obj
        self.assertEqual(
            common.get_num_vertices(bl_obj), expect_num_vert,
            "Number of imported {}'s vertices".format(obj_name))
        self.assertEqual(
            common.get_num_faces(bl_obj), expect_num_face,
            "Number of imported {}'s faces".format(obj_name))
        mqo_obj = [o for o in mqo_file.get_objects() if o.name == obj_name][0]
        self.assertTrue(common.valid_vertices(bl_obj, mqo_obj),
                        "Valid Vertices")
        self.assertTrue(common.valid_faces(bl_obj, mqo_obj), "Valid Faces")
        self.assertTrue(common.valid_vertexattr(bl_obj, mqo_obj),
                        "Valid Vertexattr")

    def _valid_material(self, mqo_file, obj_name, mtrl_name):
        bl_obj = bpy.data.objects[obj_name]
        bl_mtrl = bpy.data.materials[mtrl_name]
        mqo_obj = [o for o in mqo_file.get_objects() if o.name == obj_name][0]
        mqo_mtrl_index = [i
                          for i, m in enumerate(mqo_file.get_materials())
                          if m.name == mtrl_name][0]
        self.assertTrue(common.valid_material_assignment(
            bl_obj, mqo_obj, bl_mtrl, mqo_mtrl_index))

    def _valid_uvs(self, mqo_file, obj_name):
        bl_obj = bpy.data.objects[obj_name]
        mqo_obj = [o for o in mqo_file.get_objects() if o.name == obj_name][0]
        self.assertTrue(common.valid_uvs(bl_obj, mqo_obj))

    def _valid_mirror(self, mqo_file, obj_name):
        bl_obj = bpy.data.objects[obj_name]
        mqo_obj = [o for o in mqo_file.get_objects() if o.name == obj_name][0]
        common.valid_mirror_modifier(bl_obj.modifiers["Mirror"], mqo_obj)

    def test_import_mqo_single_object(self):
        filepath = "{}/{}/single_object.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        self.assertEqual(len(bpy.data.objects), 1,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 0,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

        mqo_file = MqoFile()
        mqo_file.load(filepath)

        self._valid_object(mqo_file, "obj1", 8, 6)

    def test_import_mqo_single_object_with_bvertex(self):
        filepath = "{}/{}/single_object_with_bvertex.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        self.assertEqual(len(bpy.data.objects), 1,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 0,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

        mqo_file = MqoFile()
        mqo_file.load(filepath)

        self._valid_object(mqo_file, "obj1", 8, 6)

    def test_import_mqo_single_object_with_edge(self):
        filepath = "{}/{}/single_object_with_edge.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        self.assertEqual(len(bpy.data.objects), 1,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 0,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

        mqo_file = MqoFile()
        mqo_file.load(filepath)

        self._valid_object(mqo_file, "obj1", 11, 6)

    def test_import_mqo_multiple_objects(self):
        filepath = "{}/{}/multiple_objects.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        self.assertEqual(len(bpy.data.objects), 2,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 0,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

        mqo_file = MqoFile()
        mqo_file.load(filepath)

        self._valid_object(mqo_file, "obj1", 8, 6)
        self._valid_object(mqo_file, "obj2", 42, 60)

    def test_import_mqo_object_with_single_material(self):
        # TODO: because blender crash at bpy.ops.object.material_slot_assign(),
        #       we can not test in Blender 2.8
        if common.check_version(2, 80, 0) >= 0:
            return

        filepath = "{}/{}/single_material.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        self.assertEqual(len(bpy.data.objects), 1,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 1,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

        mqo_file = MqoFile()
        mqo_file.load(filepath)

        self._valid_object(mqo_file, "obj1", 8, 6)
        self._valid_material(mqo_file, "obj1", "mat1")

    def test_import_mqo_object_with_single_materialex2(self):
        # TODO: because blender crash at bpy.ops.object.material_slot_assign(),
        #       we can not test in Blender 2.8
        if common.check_version(2, 80, 0) >= 0:
            return

        filepath = "{}/{}/single_material_with_materialex2.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        self.assertEqual(len(bpy.data.objects), 1,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 1,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

        mqo_file = MqoFile()
        mqo_file.load(filepath)

        self._valid_object(mqo_file, "obj1", 8, 6)
        self._valid_material(mqo_file, "obj1", "mat1")

    def test_import_mqo_object_with_multiple_materials(self):
        # TODO: because blender crash at bpy.ops.object.material_slot_assign(),
        #       we can not test in Blender 2.8
        if common.check_version(2, 80, 0) >= 0:
            return

        filepath = "{}/{}/multiple_materials.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        self.assertEqual(len(bpy.data.objects), 1,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 2,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

        mqo_file = MqoFile()
        mqo_file.load(filepath)

        self._valid_object(mqo_file, "obj1", 8, 6)
        self._valid_material(mqo_file, "obj1", "mat1")
        self._valid_material(mqo_file, "obj1", "mat2")

    def test_import_mqo_object_with_texture(self):
        # TODO: because blender crash at bpy.ops.object.material_slot_assign(),
        #       we can not test in Blender 2.8
        if common.check_version(2, 80, 0) >= 0:
            return

        filepath = "{}/{}/texture.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        self.assertEqual(len(bpy.data.objects), 1,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 1,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 1, "Number of imported images")

        mqo_file = MqoFile()
        mqo_file.load(filepath)

        self._valid_object(mqo_file, "obj1", 8, 6)
        self._valid_material(mqo_file, "obj1", "mat1")
        self._valid_uvs(mqo_file, "obj1")

    def test_import_mqo_object_with_mirrored(self):
        filepath = "{}/{}/mirrored.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        self.assertEqual(len(bpy.data.objects), 1,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 0,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

        mqo_file = MqoFile()
        mqo_file.load(filepath)

        self._valid_object(mqo_file, "obj1", 8, 5)
        self._valid_mirror(mqo_file, "obj1")

    def test_import_mqo_object_with_mirrored_multiple_axes(self):
        filepath = "{}/{}/mirrored_multiple_axes.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        self.assertEqual(len(bpy.data.objects), 1,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 0,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

        mqo_file = MqoFile()
        mqo_file.load(filepath)

        self._valid_object(mqo_file, "obj1", 8, 5)
        self._valid_mirror(mqo_file, "obj1")

    def test_import_mqo_object_with_vertexattr(self):
        filepath = "{}/{}/vertexattr.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        self.assertEqual(len(bpy.data.objects), 1,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 0,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

        mqo_file = MqoFile()
        mqo_file.load(filepath)

        self._valid_object(mqo_file, "obj1", 8, 6)

    def test_import_mqoz(self):
        filepath = "{}/{}/single_object.mqoz".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        self.assertEqual(len(bpy.data.objects), 1,
                         "Number of imported objects")
        self.assertEqual(len(bpy.data.materials), 0,
                         "Number of imported materials")
        self.assertEqual(len(bpy.data.images), 0, "Number of imported images")

        mqo_file = MqoFile()
        mqo_file.load(filepath)

        self._valid_object(mqo_file, "obj1", 8, 6)
