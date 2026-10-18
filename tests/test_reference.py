import sys
import unittest
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from facility import assess, analyze, minute_round


def visit(vid='A', appointment='2026-10-15T10:00:00', arrival='2026-10-15T10:00:00',
          check_in='2026-10-15T10:10:00', exit='2026-10-15T11:00:00', **kw):
    row = dict(visit_id=vid, visit_date=arrival[:10], trip_ref='SYN-'+vid,
               facility_code='F-A', city_state='Fictional, ZZ', visit_type='Pickup',
               trailer_context='Loaded', appointment=appointment, arrival=arrival,
               check_in=check_in, exit=exit, verified='Yes', delay_cause='None',
               delay_notes='synthetic', source='Firsthand')
    row.update(kw)
    return row


class ApprovedReferenceTests(unittest.TestCase):
    def test_T12_master_row_independent(self):
        a=visit('a')
        b=visit('b', arrival='2026-10-15T12:00:00',check_in='2026-10-15T12:15:00',exit='2026-10-15T14:00:00')
        _, s=analyze([a,b])
        self.assertEqual(s['F-A','Pickup']['valid_visits'],2)
        self.assertEqual(s['F-A','Pickup']['mean_dwell'],Decimal('90.0'))
        _, reverse=analyze([b,a])
        self.assertEqual(reverse,s)

    def test_T13_missing_appointment_excluded_from_mean(self):
        a=visit('a')
        b=visit('b',appointment=None,arrival='2026-10-15T12:00:00',check_in='2026-10-15T12:10:00',exit='2026-10-15T13:00:00')
        _,s=analyze([a,b]); q=s['F-A','Pickup']
        self.assertEqual((q['valid_visits'],q['appointment_eligible_visits'],q['mean_post_appointment_dwell']),(2,1,Decimal('60.0')))

    def test_T17_after_exit_zero_and_warning(self):
        r=assess(visit(appointment='2026-10-15T12:00:00'))
        self.assertEqual(r['quality'],'VALID')
        self.assertEqual(r['total_dwell'],Decimal('60.0'))
        self.assertTrue(r['appointment_eligible'])
        self.assertEqual(r['post_appointment_dwell'],Decimal('0.0'))
        self.assertIn('APPOINTMENT_AFTER_EXIT',r['warnings'])

    def test_T19_zero_included_missing_excluded(self):
        rows=[visit('a'),visit('b',appointment='2026-10-15T11:00:00'),visit('c',appointment=None)]
        _,s=analyze(rows); q=s['F-A','Pickup']
        self.assertEqual((q['valid_visits'],q['appointment_eligible_visits'],q['mean_post_appointment_dwell']),(3,2,Decimal('30.0')))

    def test_T20_decimal_round_half_away_from_zero(self):
        self.assertEqual(minute_round(9),Decimal('0.2'))
        self.assertEqual(minute_round(-9),Decimal('-0.2'))
        self.assertEqual(minute_round(3),Decimal('0.1'))
        self.assertEqual(minute_round(0),Decimal('0.0'))
        r=assess(visit(exit='2026-10-15T10:00:09',check_in='2026-10-15T10:00:03'))
        self.assertEqual(r['total_dwell'],Decimal('0.2'))
        self.assertEqual(r['arrival_to_check_in'],Decimal('0.1'))
        self.assertEqual(r['check_in_to_exit'],Decimal('0.1'))

    def test_T21_after_exit_zero_remains_denominator(self):
        _,s=analyze([visit('a'),visit('b',appointment='2026-10-15T12:00:00')])
        self.assertEqual(s['F-A','Pickup']['mean_post_appointment_dwell'],Decimal('30.0'))
        self.assertEqual(s['F-A','Pickup']['appointment_eligible_visits'],2)

    def test_T23_full_facility_summary(self):
        a=visit('a',delay_cause='Facility')
        b=visit('b',arrival='2026-10-15T12:00:00',check_in='2026-10-15T12:15:00',exit='2026-10-15T14:00:00')
        _,s=analyze([a,b]); q=s['F-A','Pickup']
        self.assertEqual((q['valid_visits'],q['mean_dwell'],q['max_dwell'],q['facility_coded_delays'],q['last_visit']),
                         (2,Decimal('90.0'),Decimal('120.0'),1,'2026-10-15'))

class IntegrityTests(unittest.TestCase):
    def test_early_arrival_and_signed_variance(self):
        r=assess(visit(appointment='2026-10-15T10:00:00',arrival='2026-10-15T09:30:00',check_in='2026-10-15T09:50:00',exit='2026-10-15T11:15:00'))
        self.assertEqual([r[k] for k in ('arrival_vs_appointment','arrival_to_check_in','check_in_to_exit','total_dwell','early_arrival','post_appointment_dwell')],
                         [Decimal(x) for x in ('-30','20','85','105','30','75')])

    def test_review_invalid_chronology(self):
        r=assess(visit(check_in='2026-10-15T09:00:00'))
        self.assertEqual(r['quality'],'REVIEW')
        self.assertIn('CHECK_IN_BEFORE_ARRIVAL',r['issues'])
        self.assertFalse(r['appointment_eligible'])

    def test_invalid_appointment_does_not_invalidate_total_dwell(self):
        r=assess(visit(appointment='bad-date'))
        self.assertEqual(r['quality'],'VALID')
        self.assertFalse(r['appointment_eligible'])
        self.assertIn('INVALID_APPOINTMENT',r['warnings'])

    def test_suspected_duplicates_both_count(self):
        a=visit('a'); b=visit('b')
        records,s=analyze([a,b])
        self.assertEqual(s['F-A','Pickup']['valid_visits'],2)
        self.assertIn('SUSPECTED_DUPLICATE_REVIEW',records[1]['warnings'])

    def test_reimport_confirmed_identity_not_counted(self):
        a=visit('a',source_system='synthetic',source_record_id='X1')
        b=visit('b',source_system='synthetic',source_record_id='X1',trip_ref='SYN-a')
        records,s=analyze([a,b])
        self.assertEqual(s['F-A','Pickup']['valid_visits'],1)
        self.assertIn('CONFIRMED_REIMPORT',records[1]['warnings'])
        self.assertEqual(records[1]['source']['visit_id'],'b')

    def test_human_confirmed_duplicate(self):
        a=visit('a'); b=visit('b',confirmed_duplicate_of='a')
        records,s=analyze([a,b])
        self.assertEqual(s['F-A','Pickup']['valid_visits'],1)
        self.assertIn('HUMAN_CONFIRMED_DUPLICATE',records[1]['warnings'])

    def test_unresolved_confirmation_not_excluded(self):
        a=visit('a',confirmed_duplicate_of='not-present')
        records,s=analyze([a])
        self.assertEqual(s['F-A','Pickup']['valid_visits'],1)
        self.assertIn('UNRESOLVED_DUPLICATE_REFERENCE',records[0]['warnings'])

    def test_dst_ambiguous_requires_disambiguation(self):
        r=assess(visit(arrival='2026-11-01T01:15:00',check_in='2026-11-01T01:30:00',exit='2026-11-01T02:00:00',time_zone='America/Chicago'))
        self.assertEqual(r['quality'],'REVIEW')
        self.assertIn('AMBIGUOUS_LOCAL_TIME',r['issues'])

    def test_no_valid_data_no_fabricated_average(self):
        _,s=analyze([visit(verified='No')])
        self.assertEqual(s,{})

    def test_visit_input_unchanged(self):
        original=visit('a')
        before=deepcopy(original)
        analyze([original]); self.assertEqual(original,before)

if __name__ == '__main__': unittest.main()
