import sys
import unittest
from pathlib import Path
from decimal import Decimal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from operator_model import Session, make_visit

BASE=dict(visit_date='2026-10-15',facility_code='F-A',visit_type='Pickup',
          verified='Yes',arrival='2026-10-15T10:00:00',check_in='2026-10-15T10:10:00',
          exit='2026-10-15T11:00:00',appointment='2026-10-15T10:00:00',
          delay_cause='None')

class OperatorModelTests(unittest.TestCase):
    def test_input_uses_engine_without_duplicating_rules(self):
        s=Session();s.add(BASE)
        rows,sums=s.results()
        self.assertEqual(rows[0]['total_dwell'],Decimal('60.0'))
        self.assertEqual(sums['F-A','Pickup']['mean_dwell'],Decimal('60.0'))
    def test_optional_appointment_preserves_total_dwell(self):
        s=Session();s.add(BASE);s.add(dict(BASE,appointment='',arrival='2026-10-15T12:00:00',check_in='2026-10-15T12:10:00',exit='2026-10-15T13:00:00'))
        _,sums=s.results();v=sums['F-A','Pickup']
        self.assertEqual((v['valid_visits'],v['appointment_eligible_visits'],v['mean_post_appointment_dwell']),(2,1,Decimal('60.0')))
    def test_invalid_site_time_is_review_not_exception(self):
        s=Session();s.add(dict(BASE,arrival='bad'))
        rows,sums=s.results();self.assertEqual(rows[0]['quality'],'REVIEW');self.assertEqual(sums,{})
    def test_warning_display_data_is_available(self):
        s=Session();s.add(dict(BASE,appointment='2026-10-15T12:00:00'))
        rows,_=s.results();self.assertIn('APPOINTMENT_AFTER_EXIT',rows[0]['warnings'])
        self.assertEqual(rows[0]['post_appointment_dwell'],Decimal('0.0'))
    def test_session_clears_without_writing(self):
        s=Session();s.add(BASE);s.clear();self.assertEqual(s.results(),([] ,{}))
    def test_bundled_examples(self):
        s=Session();s.load_examples(Path(__file__).resolve().parents[1]/'fixtures'/'reference_visits.json')
        _,summaries=s.results();self.assertEqual(summaries['F-A','Pickup']['valid_visits'],2)
    def test_distinct_ui_ids(self):
        s=Session();s.add(BASE);s.add(BASE)
        self.assertNotEqual(s.visits[0]['visit_id'],s.visits[1]['visit_id'])
        self.assertEqual(s.results()[1]['F-A','Pickup']['valid_visits'],2)

if __name__=='__main__': unittest.main()
