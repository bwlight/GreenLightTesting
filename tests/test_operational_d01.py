import tempfile
import unittest
from pathlib import Path
from operational_store import OperationalStore, validate

BASE={'facility_code':'OBS-01','visit_type':'Unknown','visit_status':'Incomplete'}
class DurableVisitTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'operational.sqlite3';self.store=OperationalStore(self.path)
 def tearDown(self):self.store.close();self.temp.cleanup()
 def test_create_reopen(self):
  ident=self.store.create(BASE);self.store.close();self.store=OperationalStore(self.path);self.assertEqual(self.store.get(ident)['facility_code'],'OBS-01')
 def test_duration_only(self):
  row={**BASE,'visit_status':'Completed','duration_seconds':'2530','duration_precision':'seconds','duration_source':'external stopwatch'}
  ident=self.store.create(row);m=self.store.metrics(ident);self.assertIsNone(m['total_dwell']);self.assertEqual(m['observed_duration_seconds'],'2530')
 def test_completed_requires_measurement(self):
  with self.assertRaises(ValueError):self.store.create({**BASE,'visit_status':'Completed'})
 def test_missing_offset_rejected(self):
  with self.assertRaises(ValueError):self.store.create({**BASE,'arrival':'2026-10-12T10:20:00'})
 def test_second_precision(self):
  with self.assertRaises(ValueError):self.store.create({**BASE,'arrival':'2026-10-12T10:20:00.125-05:00'})
 def test_order(self):
  with self.assertRaises(ValueError):self.store.create({**BASE,'arrival':'2026-10-12T12:00:00-05:00','exit':'2026-10-12T11:00:00-05:00'})
 def test_audit_preserves_original(self):
  ident=self.store.create(BASE)
  with self.assertRaises(ValueError):self.store.edit(ident,{**BASE,'facility_code':'OBS-02'},'')
  self.store.edit(ident,{**BASE,'facility_code':'OBS-02'},'transcription correction')
  history=self.store.history(ident)
  self.assertEqual(len(history),2);self.assertEqual(history[1]['before']['facility_code'],'OBS-01');self.assertEqual(history[1]['after']['facility_code'],'OBS-02')
 def test_search_completed(self):
  self.store.create(BASE);self.store.create({**BASE,'facility_code':'ABC','visit_status':'Completed','duration_seconds':'60','duration_precision':'minutes','duration_source':'external stopwatch'})
  self.assertEqual(len(self.store.search('ABC',True)),1);self.assertEqual(len(self.store.search('',True)),1)
 def test_engine_unchanged_adapter(self):
  row={**BASE,'visit_type':'Pickup','verified':'Yes','arrival':'2026-10-12T23:30:00-05:00','check_in':'2026-10-13T00:00:00-05:00','exit':'2026-10-13T01:00:00-05:00'}
  ident=self.store.create(row);self.assertEqual(str(self.store.metrics(ident)['total_dwell']),'90.0')
 def test_db_outside_application_path_default(self):
  from operational_store import data_path
  self.assertIn('GreenLight',str(data_path()))
if __name__=='__main__':unittest.main()
