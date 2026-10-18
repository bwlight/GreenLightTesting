"""Regression coverage for Windows timezone resources and Tk callback teardown."""
import os
import sys
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo, reset_tzpath
from datetime import datetime
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stopwatch_ui import StopwatchPanel

class WindowsRuntimePatchTests(unittest.TestCase):
    def test_bundled_zoneinfo_dst_fold(self):
        directory = Path(__file__).resolve().parents[1] / 'vendor' / 'zoneinfo'
        self.assertTrue((directory / 'America' / 'New_York').is_file())
        prior = os.environ.get('PYTHONTZPATH')
        try:
            os.environ['PYTHONTZPATH'] = str(directory)
            reset_tzpath()
            zone = ZoneInfo('America/New_York')
            a = datetime(2026,11,1,1,30,tzinfo=zone,fold=0)
            b = datetime(2026,11,1,1,30,tzinfo=zone,fold=1)
            self.assertNotEqual(a.utcoffset(),b.utcoffset())
        finally:
            if prior is None: os.environ.pop('PYTHONTZPATH',None)
            else: os.environ['PYTHONTZPATH'] = prior
            reset_tzpath()

    def test_shutdown_cancels_pending_tick(self):
        panel = object.__new__(StopwatchPanel)
        panel._tick_job = 'after#17'
        panel._shutting_down = False
        panel.after_cancel = Mock()
        panel.store = Mock()
        panel.shutdown()
        panel.after_cancel.assert_called_once_with('after#17')
        panel.store.close.assert_called_once()
        self.assertTrue(panel._shutting_down)
        self.assertIsNone(panel._tick_job)

if __name__ == '__main__': unittest.main()
