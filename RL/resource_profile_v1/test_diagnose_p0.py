"""Arithmetic diagnostic checks only; no optimizer calls."""
import itertools
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zlib
from diagnose_p0 import combine, diagnose, ROOT


def entry(h, r, value=None, bound=None, status='not_run'):
    return dict(human=h, robot=r, column=None if value is None else dict(profit=value),
                upper_bound=bound, status=status)


class DiagnosticTests(unittest.TestCase):
    def test_backward_matches_cartesian_oracle(self):
        data = dict(lines=[dict(id=x) for x in 'ABC'], human_limit=3, robot_limit=2)
        table = {x: [entry(0, 0, -2, -1), entry(1, 1, 4, 5), entry(2, 0, 7, 9)] for x in 'ABC'}
        for upper in (False, True):
            values = [sum(e['upper_bound'] if upper else e['column']['profit'] for e in es)
                      for es in itertools.product(*table.values())
                      if sum(e['human'] for e in es) <= 3 and sum(e['robot'] for e in es) <= 2]
            self.assertAlmostEqual(combine(data, table, upper)['value'], max(values))

    def test_unknown_not_infeasible(self):
        d = dict(lines=[dict(id='A')], human_limit=0, robot_limit=0)
        table = {'A': [entry(0, 0)]}
        self.assertEqual(combine(d, table, True)['bound_status'], 'unknown')
        self.assertTrue(combine(d, table, True)['possible'])
        self.assertFalse(combine(d, table)['possible'])

    def test_only_certified_infeasible_excluded(self):
        d = dict(lines=[dict(id='A')], human_limit=0, robot_limit=0)
        self.assertFalse(combine(d, {'A': [entry(0, 0, status='infeasible')]}, True)['possible'])
        self.assertTrue(combine(d, {'A': [entry(0, 0, status='time_limit')]}, True)['possible'])

    def test_capacity_and_negative_profit(self):
        d = dict(lines=[dict(id='A')], human_limit=1, robot_limit=0)
        t = {'A': [entry(0, 0, -4, -3), entry(2, 0, 100, 101)]}
        self.assertEqual(combine(d, t)['value'], -4)
        self.assertEqual(combine(d, t, True)['value'], -3)

    def test_forged_historical_query_bound_rejected(self):
        original = ROOT/'sub/stage13/evidence/robust180/tasks080_lines02_conflict_candidate_seed31__balanced_bound'
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            for name in ('instance.json', 'summary.json'):
                shutil.copyfile(original/name, folder/name)
            result = json.loads(zlib.decompress((original/'result.json.zlib').read_bytes()))
            result['base_result']['queries'][0]['upper_value'] -= 10
            (folder/'result.json.zlib').write_bytes(zlib.compress(json.dumps(result).encode()))
            with self.assertRaises(AssertionError):
                diagnose(folder)


if __name__ == '__main__':
    unittest.main(verbosity=2)
