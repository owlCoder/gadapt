"""Iteration 13 source-local fixes: static source proof only, ZERO AC calls."""
import inspect
import unittest

from research.iteration12_local_pypower_qlim_patch import runpf as previous
from research.iteration13_local_pypower_qlim_patch import runpf as revised
from research.iteration11_original_matpower_native_pf import load_original


class Iteration13RegressionTests(unittest.TestCase):
    def test_restore_generator_bus_as_integer(self):
        old=inspect.getsource(previous)
        new=inspect.getsource(revised)
        self.assertIn("bi = gen[limited[i], GEN_BUS]           ## re-adjust load,",old)
        self.assertIn("bi = gen[limited[i], GEN_BUS].astype(int)",new)

    def test_new_pv_bus_type_is_pv_constant_not_index_array(self):
        old=inspect.getsource(previous)
        new=inspect.getsource(revised)
        self.assertIn("bus[pv, BUS_TYPE] = pv",old)
        self.assertIn("bus[pv, BUS_TYPE] = PV",new)
        self.assertNotIn("bus[pv, BUS_TYPE] = pv",new)

    def test_only_two_expected_source_changes_to_q_path(self):
        old=inspect.getsource(previous)
        new=inspect.getsource(revised)
        self.assertEqual(new,old.replace(
          "bi = gen[limited[i], GEN_BUS]           ## re-adjust load,",
          "bi = gen[limited[i], GEN_BUS].astype(int)  ## re-adjust load, integer bus index"
        ).replace("bus[pv, BUS_TYPE] = pv","bus[pv, BUS_TYPE] = PV"))

    def test_original_source_slack_and_q_limits_unchanged(self):
        ppc=load_original()
        self.assertEqual(int(ppc["gen"][-1,0]),1320)
        self.assertAlmostEqual(ppc["gen"][-1,3],1)
        self.assertAlmostEqual(ppc["gen"][-1,4],-1)
        self.assertEqual(int((ppc["gen"][:,7]>0).sum()),291)

if __name__=="__main__":
    unittest.main()
