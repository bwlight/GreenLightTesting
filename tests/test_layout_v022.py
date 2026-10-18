"""Regression checks for scrollable form and fixed action bar."""
import unittest
import tkinter as tk
from tkinter import ttk
from operator_ui import OperatorUI
from green_light_theme import apply_theme

class LayoutTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root=tk.Tk()
        except tk.TclError:
            self.skipTest('Graphical display unavailable')
        apply_theme(self.root)
        self.ui=OperatorUI(self.root)

    def tearDown(self):
        self.root.destroy()

    def _render(self,width,height,scaling):
        self.root.tk.call('tk','scaling',scaling)
        self.root.geometry(f'{width}x{height}+0+0')
        self.root.update()

    def test_scroll_canvas_and_action_bar_separate(self):
        self._render(1120,790,1.0)
        self.assertIsInstance(self.ui.form_canvas,tk.Canvas)
        self.assertIsInstance(self.ui.form_scroll,ttk.Scrollbar)
        self.assertIs(self.ui.action_bar.master,self.ui.form_canvas.master.master)
        self.assertIsNot(self.ui.action_bar.master,self.ui.form)

    def test_both_other_fields_visible_and_scrollable(self):
        self.ui.vars['visit_type'].set('Other')
        self.ui.vars['source'].set('Other')
        self._render(850,620,1.0)
        for key in ('visit_type','source'):
            self.assertTrue(self.ui.other_fields[key][0].winfo_ismapped())
        self.assertGreater(self.ui.form_canvas.bbox('all')[3],self.ui.form_canvas.winfo_height())
        self.ui.form_canvas.yview_moveto(1.0)
        self.root.update()
        source_note=self.ui.other_fields['source'][0]
        self.assertLessEqual(source_note.winfo_rooty()+source_note.winfo_height(),self.ui.form_canvas.winfo_rooty()+self.ui.form_canvas.winfo_height()+4)

    def test_buttons_visible_with_expanded_fields_at_multiple_sizes(self):
        self.ui.vars['visit_type'].set('Other')
        self.ui.vars['source'].set('Other')
        for w,h,scale in [(850,620,1.0),(1000,700,1.25),(1120,790,1.5)]:
            with self.subTest(size=(w,h),scaling=scale):
                self._render(w,h,scale)
                self.assertTrue(self.ui.action_bar.winfo_ismapped())
                self.assertGreater(self.ui.action_bar.winfo_height(),15)
                self.assertLessEqual(self.ui.action_bar.winfo_rooty()+self.ui.action_bar.winfo_height(),self.root.winfo_rooty()+self.root.winfo_height())
                self.assertLessEqual(self.ui.form_canvas.winfo_rooty()+self.ui.form_canvas.winfo_height(),self.ui.action_bar.winfo_rooty())

    def test_form_width_tracks_canvas(self):
        self._render(850,620,1.0)
        self.assertEqual(int(self.ui.form_canvas.itemcget(self.ui.form_window,'width')),self.ui.form_canvas.winfo_width())
        self._render(1120,790,1.0)
        self.assertEqual(int(self.ui.form_canvas.itemcget(self.ui.form_window,'width')),self.ui.form_canvas.winfo_width())

    def test_other_text_preserved_when_toggled_in_scrolled_form(self):
        self.ui.vars['source'].set('Other')
        self.ui.other_fields['source'][1].set('Synthetic detail')
        self.ui.vars['source'].set('Firsthand')
        self.ui.vars['source'].set('Other')
        self.assertEqual(self.ui.other_fields['source'][1].get(),'Synthetic detail')

if __name__=='__main__': unittest.main()
