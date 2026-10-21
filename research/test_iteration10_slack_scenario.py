"""Unit checks for Iteration 10 slack/source limit semantics; no AC solver calls."""
import unittest
from types import SimpleNamespace
import pandas as pd

from research.iteration10_slack_scenario import (
    original_slack_preflight, ext_output)
from research.iteration9_source_generators import read_sources


def mock_model():
    return SimpleNamespace(
        bus=pd.DataFrame({"name":[1267,1319]},index=[9,10]),
        gen=pd.DataFrame({"bus":[],"in_service":[]}),
        sgen=pd.DataFrame({"bus":[9],"in_service":[True],"p_mw":[44.5]},index=[8]),
        ext_grid=pd.DataFrame({"bus":[9],"in_service":[True]},index=[0]),
        res_ext_grid=pd.DataFrame({"p_mw":[1200.],"q_mvar":[3.]},index=[0]),
    )


class Iteration10Tests(unittest.TestCase):
    def test_source_preflight_detects_2019_original_slack(self):
        gens,bus=read_sources()
        ids,ext,ref,old,sgen=original_slack_preflight(mock_model(),gens,bus)
        self.assertEqual(ids[1320],10)
        self.assertEqual(ids[1268],9)
        self.assertEqual(ext,0)
        self.assertEqual(int(ref["source_row_1based"]),298)
        self.assertEqual(int(old["gen_bus"]),1268)
        self.assertEqual(sgen,8)

    def test_does_not_silently_accept_invalid_sgen(self):
        gens,bus=read_sources()
        net=mock_model()
        net.sgen.at[8,"p_mw"]=60.
        with self.assertRaises(ValueError):
            original_slack_preflight(net,gens,bus)

    def test_ext_grid_q_and_p_limits_must_be_checked_separately(self):
        p=ext_output(mock_model(),0,dict(
            pmin_mw=0.,pmax_mw=1000.,qmin_mvar=-1.,qmax_mvar=1.))
        self.assertEqual(p["slack_p_above_max_mw"],200.)
        self.assertEqual(p["slack_q_above_max_mvar"],2.)
        self.assertEqual(p["slack_q_below_min_mvar"],0.)

if __name__=="__main__":
    unittest.main()
