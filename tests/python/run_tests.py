import os
import sys
import unittest


def test_main():
    path = os.path.dirname(__file__)
    sys.path.append(path)

    import blender_mqo_test     # pylint: disable=C0415

    test_cases = [
        blender_mqo_test.import_test.TestImportMqo,
        blender_mqo_test.export_test.TestExportMqo,
    ]

    suite = unittest.TestSuite()
    for case in test_cases:
        suite.addTest(unittest.makeSuite(case))
    ret = unittest.TextTestRunner().run(suite).wasSuccessful()
    sys.exit(not ret)


if __name__ == "__main__":
    test_main()
