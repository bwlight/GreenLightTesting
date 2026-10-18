import sys
import unittest
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from facility import assess, analyze
from test_reference import visit

class ValidationSeparationTests(unittest.TestCase):
    def test_reproduced_ambiguous_appointment_preserves_site(self):
        row = visit('amb', arrival='2026-11-01T00:15:00',
                    check_in='2026-11-01T00:30:00', exit='2026-11-01T00:45:00',
                    appointment='2026-11-01T01:30:00', time_zone='America/New_York')
        result = assess(row)
        self.assertEqual(result['quality'], 'VALID')
        self.assertEqual(result['total_dwell'], Decimal('30.0'))
        self.assertIn('AMBIGUOUS_APPOINTMENT_LOCAL_TIME', result['warnings'])
        self.assertNotIn('AMBIGUOUS_LOCAL_TIME', result['issues'])
        self.assertFalse(result['appointment_eligible'])
        self.assertIsNone(result['post_appointment_dwell'])
        _, summaries = analyze([row])
        self.assertEqual(summaries['F-A','Pickup']['valid_visits'], 1)
        self.assertEqual(summaries['F-A','Pickup']['appointment_eligible_visits'], 0)

    def test_ambiguous_site_still_requires_review(self):
        result = assess(visit(arrival='2026-11-01T01:10:00',
                    check_in='2026-11-01T01:20:00', exit='2026-11-01T01:30:00',
                    time_zone='America/New_York'))
        self.assertEqual(result['quality'], 'REVIEW')
        self.assertIn('AMBIGUOUS_LOCAL_TIME', result['issues'])

    def test_invalid_zone_with_all_aware_times_is_detected(self):
        result = assess(visit(arrival='2026-10-15T10:00:00+00:00',
                    check_in='2026-10-15T10:10:00+00:00',
                    exit='2026-10-15T11:00:00+00:00',
                    appointment='2026-10-15T10:00:00+00:00',
                    time_zone='Not/A_Zone'))
        self.assertEqual(result['quality'], 'REVIEW')
        self.assertIn('INVALID_TIME_ZONE', result['issues'])
        self.assertFalse(result['counted'])

    def test_valid_zone_all_aware_timestamps(self):
        result = assess(visit(arrival='2026-10-15T10:00:00+00:00',
                    check_in='2026-10-15T10:10:00+00:00',
                    exit='2026-10-15T11:00:00+00:00',
                    appointment='2026-10-15T10:00:00+00:00',
                    time_zone='America/New_York'))
        self.assertEqual(result['quality'], 'VALID')
        self.assertTrue(result['appointment_eligible'])

    def test_nonexistent_appointment_only_warning(self):
        result = assess(visit(arrival='2026-03-08T03:15:00',
                    check_in='2026-03-08T03:25:00', exit='2026-03-08T03:45:00',
                    appointment='2026-03-08T02:30:00', time_zone='America/New_York'))
        self.assertEqual(result['quality'], 'VALID')
        self.assertEqual(result['total_dwell'], Decimal('30.0'))
        self.assertIn('AMBIGUOUS_APPOINTMENT_LOCAL_TIME', result['warnings'])
        self.assertFalse(result['appointment_eligible'])

if __name__ == '__main__': unittest.main()
