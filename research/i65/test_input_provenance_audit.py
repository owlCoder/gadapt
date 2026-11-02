"""Synthetic I56 case-data lineage checks, no PYPOWER and no optimizer."""
from __future__ import annotations
import copy
import unittest
import numpy as np
from input_provenance_audit import LineageViolation, audit_data_lineage, numeric_fingerprint


def synthetic():
    raw = {'version':'2', 'baseMVA':100., 'bus':np.zeros((3,13)),
           'gen':np.zeros((2,10)), 'branch':np.zeros((2,13)),
           'gencost':np.zeros((2,7))}
    raw['bus'][:,0] = [1,2,3]
    raw['bus'][:,1] = [3,2,1]
    raw['bus'][:,2] = [0,12,22]
    raw['bus'][:,3] = [0,4,9]
    raw['bus'][:,5] = [0,.1,0]
    raw['bus'][:,7] = 1
    raw['bus'][:,11] = 1.1
    raw['bus'][:,12] = .9
    raw['gen'][:,0] = [1,2]
    raw['gen'][:,1] = [20,15]
    raw['gen'][:,5] = 1.0
    raw['gen'][:,7] = 1
    raw['branch'][:,0:2] = [[1,2],[2,3]]
    raw['branch'][:,2:4] = [[.01,.1],[.02,.2]]
    raw['branch'][:,8] = [0,1.]
    raw['branch'][:,10] = 1.
    seed, factor, spread = 302, 1., .1
    scaled = copy.deepcopy(raw)
    f=factor * (1 + spread * (2 * np.random.RandomState(seed).random_sample(3)-1))
    scaled['bus'][:,2] *= f
    scaled['bus'][:,3] *= f
    opf = copy.deepcopy(scaled)
    opf['gen'][:,1] = [19,16]
    candidate = copy.deepcopy(opf)
    controls=np.array([1.01,1.02,1.04,.2])
    candidate['gen'][:,5] = controls[:2]
    candidate['branch'][1,8] = controls[2]
    candidate['bus'][1,5] = controls[3]
    args=dict(load_factor=factor,spread=spread,seed=seed,
              gen_rows=[0,1],tap_rows=[1],shunt_rows=[1],
              control_values=controls)
    return raw,scaled,opf,candidate,args


class LineageAuditTests(unittest.TestCase):
    def audit(self, models=None, args=None):
        a,b,c,d,kw=synthetic()
        if models is not None:a,b,c,d=models(a,b,c,d)
        if args is not None:kw.update(args)
        return audit_data_lineage(a,b,c,d,**kw)

    def test_four_stage_success_and_control_accounting(self):
        x=self.audit()
        self.assertEqual(x['schema'],'GADAPT_I65_ORPD_INPUT_LINEAGE_V1')
        self.assertEqual(x['control_counts'],{'vg':2,'tap':1,'shunt':1})
        self.assertEqual(len(x['stages']),4)

    def test_deterministic_fingerprints(self):
        self.assertEqual(self.audit(),self.audit())

    def test_fingerprint_refuses_nonfinite(self):
        raw,*_=synthetic()
        raw['bus'][0,2]=float('nan')
        with self.assertRaises(LineageViolation):numeric_fingerprint(raw)

    def test_fingerprint_detects_subtle_numeric_change(self):
        a,*_=synthetic()
        b=copy.deepcopy(a)
        b['branch'][1,3]+=1e-12
        self.assertNotEqual(numeric_fingerprint(a),numeric_fingerprint(b))

    def test_negative_spread_refused(self):
        with self.assertRaises(LineageViolation):self.audit(args={'spread':-0.01})

    def test_wrong_seed_changes_load_lineage(self):
        with self.assertRaisesRegex(LineageViolation,'scaled PD/QD'):
            self.audit(args={'seed':303})

    def test_scaled_load_tamper_fails(self):
        def mutate(a,b,c,d):
            b['bus'][1,2]+=.01
            return a,b,c,d
        with self.assertRaisesRegex(LineageViolation,'scaled PD/QD'):self.audit(models=mutate)

    def test_scaled_branch_tamper_fails(self):
        def mutate(a,b,c,d):
            b['branch'][0,2]+=.01
            return a,b,c,d
        with self.assertRaises(LineageViolation):self.audit(models=mutate)

    def test_opf_can_modify_pg_only(self):
        v=self.audit()
        self.assertNotEqual(v['stages']['scaled'],v['stages']['post_opf'])

    def test_opf_qg_falsification_detected(self):
        def mutate(a,b,c,d):
            c['gen'][0,2]+=.1
            return a,b,c,d
        with self.assertRaisesRegex(LineageViolation,'OPF handoff'):self.audit(models=mutate)

    def test_control_voltage_extra_row_rejected(self):
        def mutate(a,b,c,d):
            d['gen'][0,2]+=.1
            return a,b,c,d
        with self.assertRaisesRegex(LineageViolation,'control-stage gen'):self.audit(models=mutate)

    def test_control_unauthorized_line_rating_change(self):
        def mutate(a,b,c,d):
            d['branch'][1,5]+=.1
            return a,b,c,d
        with self.assertRaisesRegex(LineageViolation,'control-stage branch'):self.audit(models=mutate)

    def test_control_unauthorized_load_change(self):
        def mutate(a,b,c,d):
            d['bus'][1,3]+=.1
            return a,b,c,d
        with self.assertRaisesRegex(LineageViolation,'control-stage bus'):self.audit(models=mutate)

    def test_cost_matrix_must_stay_equal(self):
        def mutate(a,b,c,d):
            c['gencost'][0,1]=1.
            return a,b,c,d
        with self.assertRaisesRegex(LineageViolation,'generator cost'):self.audit(models=mutate)

    def test_missing_control_index_refused(self):
        with self.assertRaises(LineageViolation):
            self.audit(args={'tap_rows':[999]})

    def test_duplicate_control_index_refused(self):
        with self.assertRaises(LineageViolation):
            self.audit(args={'gen_rows':[0,0]})

    def test_unexpected_case_key_refused(self):
        def mutate(a,b,c,d):
            d['fake']='cannot insert'
            return a,b,c,d
        with self.assertRaises(LineageViolation):self.audit(models=mutate)


if __name__=='__main__':unittest.main()
