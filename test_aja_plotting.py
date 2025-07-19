import unittest
from aja_plotting import *


class TestAJAPlotting(unittest.TestCase):
    def setUp(self):
        self.file_path = r"sample_folder\datalogs\20250714_XRR04_S055_30C_3nm Ta_600C_97_nm_Ta_TaOx_14-Jul-25_ 4_55_14 PM.csv"
        self.aja_df = AJA_df(self.file_path)

    def test_get_layer_num(self):
        self.assertEqual(self.aja_df.get_layer_num(), 15)


if __name__ == "__main__":
    unittest.main()
