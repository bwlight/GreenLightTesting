import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from facility import analyze
from test_reference import visit

class OrderIdentityTests(unittest.TestCase):
    def check_orders(self, rows, expected_count, expected_mean=None):
        first, summary = analyze(rows)
        second, reverse = analyze(list(reversed(rows)))
        self.assertEqual(summary, reverse)
        self.assertEqual(summary['F-A', 'Pickup']['valid_visits'], expected_count)
        if expected_mean is not None:
            self.assertEqual(summary['F-A', 'Pickup']['mean_dwell'], expected_mean)
        for result_set in (first, second):
            self.assertEqual({r['source']['visit_id'] for r in result_set if r['counted']},
                             {r['source']['visit_id'] for r in first if r['counted']})

    def test_confirmed_reimport_different_dwell_conflict_keeps_both(self):
        a = visit('a', source_system='sim', source_record_id='R1')
        b = visit('b', source_system='sim', source_record_id='R1', exit='2026-10-15T12:00:00')
        self.check_orders([a,b], 2)
        records, _ = analyze([a,b])
        self.assertTrue(all('SOURCE_ID_CONFLICT_REVIEW' in r['warnings'] for r in records))

    def test_confirmed_reimport_identical_payload_keeper_stable(self):
        a = visit('a', source_system='sim', source_record_id='R1')
        b = visit('b', source_system='sim', source_record_id='R1', trip_ref='SYN-a')
        self.check_orders([a,b], 1)
        records,_=analyze([b,a])
        self.assertEqual({r['source']['visit_id'] for r in records if r['counted']},{'a'})

    def test_human_confirmation_forward_reference(self):
        a = visit('a')
        b = visit('b', confirmed_duplicate_of='a', exit='2026-10-15T12:00:00')
        self.check_orders([a,b], 1)

    def test_identical_timestamps_without_identity_both_count(self):
        self.check_orders([visit('a'),visit('b')],2)

    def test_conflicting_visit_ids_do_not_drop_data(self):
        a = visit('a')
        b = visit('a',exit='2026-10-15T12:00:00')
        self.check_orders([a,b],2)

    def test_unresolved_confirmation_remains_counted(self):
        self.check_orders([visit('a',confirmed_duplicate_of='missing')],1)

    def test_mutual_confirmation_cycle_not_auto_excluded(self):
        self.check_orders([visit('a',confirmed_duplicate_of='b'),visit('b',confirmed_duplicate_of='a')],2)

if __name__ == '__main__': unittest.main()
