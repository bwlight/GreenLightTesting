import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from stopwatch_store import StopwatchStore, validate_stamp

A='2026-10-15T23:59:05-05:00'
C='2026-10-16T00:00:14-05:00'
X='2026-10-16T01:00:26-05:00'

class StopwatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'visits.db'
        self.s=StopwatchStore(self.path)
    def tearDown(self):
        self.s.close();self.tmp.cleanup()
    def start(self):
        return self.s.start('SYN-A','Pickup',stamp=A)
    def test_capture_precision_and_overnight(self):
        v=self.start();self.s.capture(v,'check_in',C);self.s.capture(v,'exit',X)
        result=self.s.assessed(v)
        self.assertEqual(result['quality'],'VALID')
        self.assertEqual(str(result['total_dwell']),'61.4')
        self.assertEqual(self.s.events(v)['arrival']['captured_at'],A)
    def test_restart_recovery(self):
        v=self.start();self.s.close();self.s=StopwatchStore(self.path)
        self.assertEqual(self.s.active()['id'],v)
        self.s.capture(v,'check_in',C)
        self.assertEqual(self.s.events(v)['check_in']['effective_at'],C)
    def test_prevent_duplicate_capture(self):
        v=self.start();self.s.capture(v,'check_in',C)
        with self.assertRaises(ValueError):self.s.capture(v,'check_in',C)
        self.assertEqual(len(self.s.events(v)),2)
    def test_order_enforced(self):
        v=self.start()
        with self.assertRaises(ValueError):self.s.capture(v,'exit',X)
        with self.assertRaises(ValueError):self.s.capture(v,'check_in','2026-10-15T23:00:00-05:00')
    def test_only_one_active(self):
        self.start()
        with self.assertRaises(ValueError):self.start()
    def test_completed_allows_new(self):
        v=self.start();self.s.capture(v,'check_in',C);self.s.capture(v,'exit',X)
        self.assertIsNone(self.s.active())
        self.assertNotEqual(self.start(),v)
    def test_correction_preserves_original_and_audit(self):
        v=self.start();self.s.capture(v,'check_in',C)
        new='2026-10-16T00:00:20-05:00'
        self.s.correct(v,'check_in',new,'Driver verified gate slip')
        ev=self.s.events(v)['check_in']
        self.assertEqual(ev['captured_at'],C)
        self.assertEqual(ev['effective_at'],new)
        history=self.s.history(v)
        self.assertEqual(len(history),1)
        self.assertEqual(history[0]['original_capture'],C)
        self.assertEqual(history[0]['reason'],'Driver verified gate slip')
    def test_repeated_corrections_audited(self):
        v=self.start();self.s.capture(v,'check_in',C)
        self.s.correct(v,'check_in','2026-10-16T00:00:20-05:00','First correction')
        self.s.correct(v,'check_in','2026-10-16T00:00:30-05:00','Second correction')
        self.assertEqual(len(self.s.history(v)),2)
        self.assertEqual(self.s.history(v)[1]['original_capture'],C)
    def test_correction_reason_required(self):
        v=self.start()
        with self.assertRaises(ValueError):self.s.correct(v,'arrival',A,'   ')
    def test_correction_order_rejected(self):
        v=self.start();self.s.capture(v,'check_in',C);self.s.capture(v,'exit',X)
        with self.assertRaises(ValueError):self.s.correct(v,'check_in','2026-10-16T02:00:00-05:00','bad')
        self.assertEqual(self.s.history(v),[])
    def test_missing_offset_rejected(self):
        with self.assertRaises(ValueError):validate_stamp('2026-10-15T23:59:05')
    def test_fractional_second_rejected(self):
        with self.assertRaises(ValueError):validate_stamp('2026-10-15T23:59:05.123-05:00')
    def test_offset_instant_order(self):
        v=self.start()
        self.s.capture(v,'check_in','2026-10-16T05:00:00+00:00')
        self.assertIn('check_in',self.s.events(v))
    def test_db_durable_after_close(self):
        v=self.start();self.s.capture(v,'check_in',C);self.s.close();self.s=StopwatchStore(self.path)
        self.assertEqual(self.s.events(v)['check_in']['captured_at'],C)
    def test_calculation_engine_unmodified_delegate(self):
        v=self.start();self.s.capture(v,'check_in',C);self.s.capture(v,'exit',X)
        self.assertEqual(self.s.assessed(v)['total_dwell'],__import__('facility').assess(self.s.assessed(v)['source'])['total_dwell'])

if __name__=='__main__': unittest.main()
