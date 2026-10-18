import tempfile, unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
from operational_store import OperationalStore
from operational_capture import CaptureService

class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'operational.sqlite3'
        self.store=OperationalStore(self.path)
        self.t=datetime(2026,10,12,23,59,58,tzinfo=timezone(timedelta(hours=-5)))
        self.svc=CaptureService(self.store,lambda:self.t)
    def tearDown(self):self.store.close();self.temp.cleanup()
    def start(self):return self.svc.new_arrival('TEST01','Pickup','Loaded')[0]
    def test_durable_arrival_and_recovery(self):
        ident=self.start();self.store.close();self.store=OperationalStore(self.path)
        self.svc=CaptureService(self.store,lambda:self.t)
        self.assertEqual(self.svc.unfinished()[0][0],ident)
        self.assertEqual(self.store.get(ident)['verified'],'No')
    def test_duplicate_and_overnight(self):
        ident=self.start();self.t+=timedelta(seconds=5)
        self.svc.capture(ident,'check_in')
        with self.assertRaises(ValueError):self.svc.capture(ident,'check_in')
        self.t+=timedelta(minutes=2);self.svc.capture(ident,'exit')
        self.assertEqual(self.store.get(ident)['visit_status'],'Completed')
        self.assertEqual(len(self.store.history(ident)),3)
        self.assertEqual(self.svc.unfinished(),[])
    def test_missing_check_in(self):
        ident=self.start();self.t+=timedelta(minutes=5);self.svc.capture(ident,'exit')
        self.assertEqual(self.store.get(ident)['check_in'],'')
    def test_backwards_time_rejected(self):
        ident=self.start();self.t-=timedelta(seconds=1)
        with self.assertRaises(ValueError):self.svc.capture(ident,'exit')
        self.assertEqual(self.store.get(ident)['exit'],'')
    def test_offset_change_audited(self):
        ident=self.start();self.t=self.t.astimezone(timezone(timedelta(hours=-4)))+timedelta(minutes=1)
        _,flag=self.svc.capture(ident,'exit');self.assertTrue(flag)
        self.assertIn('OFFSET_CHANGED_REVIEW',self.store.history(ident)[-1]['reason'])
    def test_correction_and_manual_compatibility(self):
        ident=self.start();before=self.store.get(ident);after=dict(before);after['arrival']='2026-10-12T23:59:57-05:00'
        self.store.edit(ident,after,'Clock was one second fast')
        self.assertEqual(self.store.history(ident)[-1]['before']['arrival'],before['arrival'])
        self.assertEqual(self.store.history(ident)[-1]['reason'],'Clock was one second fast')
    def test_invalid_facility_and_sequence(self):
        with self.assertRaises(ValueError):self.svc.new_arrival('','Pickup','Loaded')
        ident=self.start();self.t+=timedelta(seconds=1)
        self.svc.capture(ident,'exit')
        with self.assertRaises(ValueError):self.svc.capture(ident,'check_in')

class DelayTests(unittest.TestCase):
    def test_optional_delay_is_audited_without_correction_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=OperationalStore(Path(tmp)/'db.sqlite3')
            service=CaptureService(store,lambda:datetime(2026,10,12,10,0,0,tzinfo=timezone.utc))
            ident,_=service.new_arrival('TEST02','Drop-off','Empty')
            service.record_delay(ident,'Trailer missing / wrong location','Yard B')
            self.assertEqual(store.get(ident)['delay_cause'],'Equipment')
            self.assertIn('Yard B',store.get(ident)['delay_notes'])
            self.assertEqual(store.history(ident)[-1]['reason'],'NORMAL_DELAY_OBSERVATION')
            with self.assertRaises(ValueError):service.record_delay(ident,'No problems')
            store.close()
