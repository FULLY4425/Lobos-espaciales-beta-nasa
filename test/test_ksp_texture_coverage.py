import io
import unittest
from scripts.ksp_texture_coverage import build_coverage

class TextureCoverageTests(unittest.TestCase):
    def test_masks_flip_north_south_and_compress_without_filling_holes(self):
        source=io.StringIO('Row,Column,Lat,Long,Height\n0,1,0,0,10\n0,2,0,0,10\n0,4,0,0,10\n2,0,0,0,10\n')
        self.assertEqual(build_coverage(source,5,3),dict(width=5,height=3,rows={'0':[[0,0]],'2':[[1,2],[4,4]]}))

    def test_indices_outside_declared_image_are_rejected(self):
        with self.assertRaises(ValueError):
            build_coverage(io.StringIO('Row,Column\n3,0\n'),5,3)
