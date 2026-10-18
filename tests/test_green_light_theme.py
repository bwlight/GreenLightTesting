import unittest
import tkinter as tk
from tkinter import ttk
from green_light_theme import apply_theme, CHARCOAL, ELECTRIC_GREEN, TEXT, DARK_TEXT


class ThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
        except tk.TclError:
            raise unittest.SkipTest('GUI display unavailable')
        cls.style = apply_theme(cls.root)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'root'): cls.root.destroy()

    def test_dark_background(self):
        self.assertEqual(self.root.cget('bg').lower(), CHARCOAL.lower())

    def test_primary_action_color(self):
        self.assertEqual(self.style.lookup('Primary.TButton','background').lower(), ELECTRIC_GREEN.lower())

    def test_primary_action_foreground(self):
        self.assertEqual(self.style.lookup('Primary.TButton','foreground').lower(), DARK_TEXT.lower())

    def test_readable_label(self):
        self.assertEqual(self.style.lookup('TLabel','foreground').lower(), TEXT.lower())

    def test_selected_tab_style(self):
        self.assertIn(('selected', ELECTRIC_GREEN), self.style.map('TNotebook.Tab','background'))

    def test_treeview_selection(self):
        self.assertTrue(self.style.map('Treeview','background'))

    def test_ui_constructs_and_uses_primary_action(self):
        from operator_ui import OperatorUI
        ui = OperatorUI(self.root)
        self.assertEqual(len(ui.date_controls), 5)
        self.assertTrue(any(isinstance(w,ttk.Button) and w.cget('style')=='Primary.TButton' for w in ui.action_bar.winfo_children()))
