import tempfile,unittest,tkinter as tk
from pathlib import Path
from unittest.mock import patch
from operational_ui import OperationalPanel

class OperationalCaptureGuiTests(unittest.TestCase):
    def test_buttons_visible_and_capture_operational_record(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch('operational_ui.OperationalStore',side_effect=lambda: __import__('operational_store').OperationalStore(Path(folder)/'real.sqlite3')):
                root=tk.Tk();root.geometry('1150x820')
                panel=OperationalPanel(root);panel.pack(fill='both',expand=True);root.update()
                try:
                    for key in ('arrival','check_in','exit'):
                        self.assertTrue(panel.capture_buttons[key].winfo_ismapped())
                    panel.quick_facility.set('SYNTHETIC01')
                    panel.capture_event('arrival')
                    self.assertIsNotNone(panel.active_visit)
                    panel.capture_event('check_in')
                    panel.capture_event('exit')
                    self.assertEqual(panel.store.get(panel.active_visit)['visit_status'],'Completed')
                    self.assertEqual(len(panel.store.history(panel.active_visit)),3)
                finally:
                    panel.shutdown();root.destroy()
