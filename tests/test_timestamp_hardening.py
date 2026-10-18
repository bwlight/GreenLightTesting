import sys
import unittest
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from facility import assess, analyze
from test_reference import visit

class TimestampHardeningTests(unittest.TestCase):
    def test_mixed_appointment_naive_site_aware_is_safe(self):
        r=assess(visit(arrival='2026-10-15T10:00:00+00:00', check_in='2026-10-15T10:10:00+00:00', exit='2026-10-15T11:00:00+00:00', appointment='2026-10-15T10:00:00'))
        self.assertEqual(r['quality'],'VALID')
        self.assertEqual(r['total_dwell'],Decimal('60.0'))
        self.assertFalse(r['appointment_eligible'])
        self.assertIsNone(r['post_appointment_dwell'])
        self.assertIn('MIXED_APPOINTMENT_TIMEZONE',r['warnings'])

    def test_mixed_appointment_aware_site_naive_is_safe(self):
        r=assess(visit(appointment='2026-10-15T10:00:00+00:00'))
        self.assertEqual(r['quality'],'VALID')
        self.assertFalse(r['appointment_eligible'])
        self.assertIn('MIXED_APPOINTMENT_TIMEZONE',r['warnings'])

    def test_mixed_site_timestamps_review_not_exception(self):
        r=assess(visit(check_in='2026-10-15T10:10:00+00:00'))
        self.assertEqual(r['quality'],'REVIEW')
        self.assertIn('MIXED_TIMEZONE_REPRESENTATION',r['issues'])
        self.assertFalse(r['counted'])

    def test_aware_offsets_compare_as_instants(self):
        r=assess(visit(appointment='2026-10-15T09:00:00-01:00',arrival='2026-10-15T10:00:00+00:00',check_in='2026-10-15T11:10:00+01:00',exit='2026-10-15T07:00:00-04:00'))
        self.assertEqual(r['quality'],'VALID')
        self.assertEqual(r['total_dwell'],Decimal('60.0'))
        self.assertEqual(r['post_appointment_dwell'],Decimal('60.0'))

    def test_bad_appointment_values_do_not_poison_total_dwell(self):
        for bad in ([],{},17,True,'not-a-date','2026-02-30T10:00:00','2026-10-15T25:00:00'):
            with self.subTest(bad=bad):
                r=assess(visit(appointment=bad))
                self.assertEqual(r['quality'],'VALID')
                self.assertFalse(r['appointment_eligible'])
                self.assertIn('INVALID_APPOINTMENT',r['warnings'])

    def test_bad_site_values_review_without_crash(self):
        for bad in ([],{},17,True,'not-a-date','2026-02-30T10:00:00'):
            with self.subTest(bad=bad):
                r=assess(visit(check_in=bad))
                self.assertEqual(r['quality'],'REVIEW')
                self.assertIn('MISSING_OR_INVALID_SITE_TIME',r['issues'])

    def test_mixed_appointment_excluded_from_summary_denominator(self):
        mixed=visit('b',appointment='2026-10-15T10:00:00+00:00')
        _,s=analyze([visit('a'),mixed])
        q=s['F-A','Pickup']
        self.assertEqual((q['valid_visits'],q['appointment_eligible_visits'],q['mean_post_appointment_dwell']), (2,1,Decimal('60.0')))

    def test_malformed_zone_does_not_crash(self):
        for bad in ('Not/A_Zone', [], {'bad':1}):
            with self.subTest(bad=bad):
                r=assess(visit(time_zone=bad))
                self.assertEqual(r['quality'],'REVIEW')
                self.assertIn('INVALID_TIME_ZONE',r['issues'])

    def test_after_exit_aware_appointment_preserves_zero(self):
        r=assess(visit(arrival='2026-10-15T10:00:00+00:00',check_in='2026-10-15T10:10:00+00:00',exit='2026-10-15T11:00:00+00:00',appointment='2026-10-15T12:00:00+00:00'))
        self.assertEqual(r['quality'],'VALID')
        self.assertEqual(r['post_appointment_dwell'],Decimal('0.0'))
        self.assertIn('APPOINTMENT_AFTER_EXIT',r['warnings'])

if __name__=='__main__': unittest.main()
