import os

import bpy

from blender_mqo.utils.mqo_file import MqoFile
from . import common

EXPORTED_DIR = "exported"
MQO_FILE_DIR = "mqo_files"


class TestExportMqo(common.TestBase):
    module_name = "export_scene"
    idname = [
        ('OPERATOR', 'export_scene.blmqo_ot_export_mqo')
    ]

    def setUpEachMethod(self):
        if not os.path.exists(EXPORTED_DIR):
            os.makedirs(EXPORTED_DIR)

    def _is_same_mtrl(self, material_1, material_2):
        self.assertTrue(common.is_same(material_1.name, material_2.name))
        self.assertTrue(common.is_same(material_1.color[0:3],
                                       material_2.color[0:3]))
        self.assertTrue(
            common.is_same(material_1.specular, material_2.specular))
        self.assertTrue(
            common.is_same(material_1.emissive, material_2.emissive))
        if common.check_version(2, 80, 0) < 0:
            self.assertTrue(
                common.is_same(material_1.diffuse, material_2.diffuse))
            self.assertTrue(
                common.is_same(material_1.ambient, material_2.ambient))

    def _is_same_object(self, obj_1, obj_2):
        self.assertTrue(common.is_same(obj_1.name, obj_2.name))
        self.assertTrue(common.is_same(obj_1.scale, obj_2.scale))
        self.assertTrue(common.is_same(obj_1.rotation, obj_2.rotation))
        self.assertTrue(common.is_same(obj_1.translation,
                                       obj_2.translation))

        self.assertEqual(len(obj_1.get_vertices()), len(obj_2.get_vertices()))
        for vert_1, vert_2 in zip(obj_1.get_vertices(), obj_2.get_vertices()):
            self.assertTrue(common.is_same(vert_1, vert_2))

        self.assertEqual(len(obj_1.get_faces(uniq=True)),
                         len(obj_2.get_faces(uniq=True)))
        for face_1, face_2 in zip(obj_1.get_faces(uniq=True),
                                  obj_2.get_faces(uniq=True)):
            self.assertTrue(face_1.is_same(face_2))

    def _is_same_mqo_file(self, mqo_file_1, mqo_file_2):
        self.assertTrue(common.is_same(mqo_file_1.header, mqo_file_2.header))
        self.assertTrue(common.is_same(mqo_file_1.version, mqo_file_2.version))
        self.assertTrue(common.is_same(mqo_file_1.format, mqo_file_2.format))

        self.assertEqual(len(mqo_file_1.get_materials()),
                         len(mqo_file_2.get_materials()))
        for mtrl_1, mtrl_2 in zip(mqo_file_1.get_materials(),
                                  mqo_file_2.get_materials()):
            self._is_same_mtrl(mtrl_1, mtrl_2)

        self.assertEqual(len(mqo_file_1.get_objects()),
                         len(mqo_file_2.get_objects()))
        for obj_1, obj_2 in zip(mqo_file_1.get_objects(),
                                mqo_file_2.get_objects()):
            self._is_same_object(obj_1, obj_2)

    def test_export_no_object(self):
        export_filepath = "{}/no_object.mqo".format(EXPORTED_DIR, MQO_FILE_DIR)
        bpy.ops.export_scene.blmqo_ot_export_mqo('EXEC_DEFAULT',
                                                 filepath=export_filepath)
        export_mqo_file = MqoFile()
        export_mqo_file.load(export_filepath)

        import_filepath = "{}/{}/scene.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        import_mqo_file = MqoFile()
        import_mqo_file.load(import_filepath)

        self._is_same_mqo_file(export_mqo_file, import_mqo_file)

    def test_export_single_object(self):
        import_filepath = "{}/{}/single_object.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=import_filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        export_filepath = "{}/single_object.mqo".format(EXPORTED_DIR,
                                                        MQO_FILE_DIR)
        bpy.ops.export_scene.blmqo_ot_export_mqo('EXEC_DEFAULT',
                                                 filepath=export_filepath,
                                                 add_export_prefix=False,
                                                 export_prefix="")
        export_mqo_file = MqoFile()
        export_mqo_file.load(export_filepath)

        import_mqo_file = MqoFile()
        import_mqo_file.load(import_filepath)

        self._is_same_mqo_file(export_mqo_file, import_mqo_file)

    def test_export_multiple_objects(self):
        import_filepath = "{}/{}/multiple_objects.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=import_filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        export_filepath = "{}/multiple_objects.mqo".format(EXPORTED_DIR,
                                                           MQO_FILE_DIR)
        bpy.ops.export_scene.blmqo_ot_export_mqo('EXEC_DEFAULT',
                                                 filepath=export_filepath,
                                                 add_export_prefix=False,
                                                 export_prefix="")
        export_mqo_file = MqoFile()
        export_mqo_file.load(export_filepath)

        import_mqo_file = MqoFile()
        import_mqo_file.load(import_filepath)

        self._is_same_mqo_file(export_mqo_file, import_mqo_file)

    def test_export_mqo_object_with_single_material(self):
        # TODO: because blender crash at bpy.ops.object.material_slot_assign(),
        #       we can not test in Blender 2.8
        if common.check_version(2, 80, 0) >= 0:
            return

        import_filepath = "{}/{}/single_material.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=import_filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        export_filepath = "{}/single_material.mqo".format(EXPORTED_DIR,
                                                          MQO_FILE_DIR)
        bpy.ops.export_scene.blmqo_ot_export_mqo('EXEC_DEFAULT',
                                                 filepath=export_filepath,
                                                 add_export_prefix=False,
                                                 export_prefix="")
        export_mqo_file = MqoFile()
        export_mqo_file.load(export_filepath)

        import_mqo_file = MqoFile()
        import_mqo_file.load(import_filepath)

        self._is_same_mqo_file(export_mqo_file, import_mqo_file)

    def test_export_mqo_object_with_multiple_materials(self):
        # TODO: because blender crash at bpy.ops.object.material_slot_assign(),
        #       we can not test in Blender 2.8
        if common.check_version(2, 80, 0) >= 0:
            return

        import_filepath = "{}/{}/multiple_materials.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=import_filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        export_filepath = "{}/multiple_materials.mqo".format(EXPORTED_DIR,
                                                             MQO_FILE_DIR)
        bpy.ops.export_scene.blmqo_ot_export_mqo('EXEC_DEFAULT',
                                                 filepath=export_filepath,
                                                 add_export_prefix=False,
                                                 export_prefix="")
        export_mqo_file = MqoFile()
        export_mqo_file.load(export_filepath)

        import_mqo_file = MqoFile()
        import_mqo_file.load(import_filepath)

        self._is_same_mqo_file(export_mqo_file, import_mqo_file)

    def test_export_mqo_object_with_texture(self):
        # TODO: because blender crash at bpy.ops.object.material_slot_assign(),
        #       we can not test in Blender 2.8
        if common.check_version(2, 80, 0) >= 0:
            return

        import_filepath = "{}/{}/texture.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=import_filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        export_filepath = "{}/texture.mqo".format(EXPORTED_DIR, MQO_FILE_DIR)
        bpy.ops.export_scene.blmqo_ot_export_mqo('EXEC_DEFAULT',
                                                 filepath=export_filepath,
                                                 add_export_prefix=False,
                                                 export_prefix="")
        export_mqo_file = MqoFile()
        export_mqo_file.load(export_filepath)

        import_mqo_file = MqoFile()
        import_mqo_file.load(import_filepath)

        self._is_same_mqo_file(export_mqo_file, import_mqo_file)

    def test_export_mqo_object_with_mirrored(self):
        import_filepath = "{}/{}/mirrored.mqo".format(
            os.path.dirname(os.path.abspath(__file__)), MQO_FILE_DIR)
        bpy.ops.import_scene.blmqo_ot_import_mqo('EXEC_DEFAULT',
                                                 filepath=import_filepath,
                                                 add_import_prefix=False,
                                                 import_prefix="")

        export_filepath = "{}/mirrored.mqo".format(EXPORTED_DIR, MQO_FILE_DIR)
        bpy.ops.export_scene.blmqo_ot_export_mqo('EXEC_DEFAULT',
                                                 filepath=export_filepath,
                                                 add_export_prefix=False,
                                                 export_prefix="")
        export_mqo_file = MqoFile()
        export_mqo_file.load(export_filepath)

        import_mqo_file = MqoFile()
        import_mqo_file.load(import_filepath)

        self.assertTrue(common.is_same(export_mqo_file.header,
                                       import_mqo_file.header))
        self.assertTrue(common.is_same(export_mqo_file.version,
                                       import_mqo_file.version))
        self.assertTrue(common.is_same(export_mqo_file.format,
                                       import_mqo_file.format))

        self.assertEqual(len(export_mqo_file.get_materials()),
                         len(import_mqo_file.get_materials()))
        for exp_mtrl, imp_mtrl in zip(export_mqo_file.get_materials(),
                                      import_mqo_file.get_materials()):
            self._is_same_mtrl(exp_mtrl, imp_mtrl)

        self.assertEqual(len(export_mqo_file.get_objects()),
                         len(import_mqo_file.get_objects()))
        for exp_obj, imp_obj in zip(export_mqo_file.get_objects(),
                                    import_mqo_file.get_objects()):
            self.assertTrue(common.is_same(exp_obj.name, imp_obj.name))
            self.assertTrue(common.is_same(exp_obj.scale, imp_obj.scale))
            self.assertTrue(common.is_same(exp_obj.rotation, imp_obj.rotation))
            self.assertTrue(common.is_same(exp_obj.translation,
                                           imp_obj.translation))
            self.assertEqual(len(exp_obj.get_vertices()), 12)
            for exp_vert, imp_vert in zip(exp_obj.get_vertices(),
                                          imp_obj.get_vertices()[0:4]):
                self.assertTrue(common.is_same(exp_vert, imp_vert))
            self.assertEqual(len(exp_obj.get_faces(uniq=True)), 10)
            self.assertTrue(exp_obj.get_faces(uniq=True)[0]
                            .is_same(imp_obj.get_faces(uniq=True)[0]))
