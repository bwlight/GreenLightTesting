"""Regression: stopwatch must be mounted and its timer cancelled on parent teardown."""
import tempfile
import unittest
import tkinter as tk
from pathlib import Path
from unittest.mock import patch
from tkinter import ttk
from operator_ui import OperatorUI
from stopwatch_ui import StopwatchPanel

class StopwatchGuiMountTests(unittest.TestCase):
    def test_tab_four_mounted_controls_and_capture(self):
        root=tk.Tk()
        try:
            with tempfile.TemporaryDirectory() as temp:
                with patch('operator_ui.ROOT',Path(temp)):
                    ui=OperatorUI(root)
                root.update()
                notebook=next(w for w in root.winfo_children() if isinstance(w,ttk.Panedwindow))
                lower=next(w for w in notebook.winfo_children() if isinstance(w,ttk.Notebook))
                lower.select(2)
                root.update()
                self.assertTrue(ui.stopwatch.winfo_ismapped())
                self.assertTrue(ui.stopwatch.start_button.winfo_ismapped())
                self.assertTrue(ui.stopwatch.check_button.winfo_ismapped())
                self.assertTrue(ui.stopwatch.exit_button.winfo_ismapped())
                self.assertEqual(ui.stopwatch.elapsed.get(),'00:00')
                ui.stopwatch.start()
                self.assertIsNotNone(ui.stopwatch.current_id)
                ui.stopwatch.capture('check_in')
                self.assertIn('check_in',ui.stopwatch.store.events(ui.stopwatch.current_id))
                # root.destroy bypasses WM_DELETE_WINDOW; must still cancel timer.
                root.destroy()
                self.assertTrue(ui.stopwatch._shutting_down)
                self.assertIsNone(ui.stopwatch._tick_job)
                root.update()
        finally:
            try: root.destroy()
            except tk.TclError: pass

    def test_direct_panel_destroy_cancels_tick(self):
        root=tk.Tk()
        try:
            with tempfile.TemporaryDirectory() as temp:
                panel=StopwatchPanel(root,Path(temp)/'synthetic.sqlite3')
                panel.pack()
                root.update()
                self.assertIsNotNone(panel._tick_job)
                panel.destroy()
                self.assertIsNone(panel._tick_job)
                root.update()
        finally:
            root.destroy()
