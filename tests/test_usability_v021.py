import unittest
import tkinter as tk
from tkinter import ttk
from operator_model import make_visit
from date_controls import DatePicker, DateTimePicker
from operator_ui import OperatorUI, DEFAULTS
from green_light_theme import apply_theme

class UsabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root=tk.Tk()
            apply_theme(cls.root)
        except tk.TclError:
            raise unittest.SkipTest('GUI display unavailable')

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,'root'): cls.root.destroy()

    def test_other_fields_present_for_all_supported_choices(self):
        ui=OperatorUI(self.root)
        self.assertEqual(set(ui.other_fields), {'visit_type','source'})

    def test_other_reveals_and_preserves_text(self):
        ui=OperatorUI(self.root)
        frame,value=ui.other_fields['visit_type']
        ui.vars['visit_type'].set('Other')
        self.assertTrue(frame.winfo_manager())
        value.set('Fictional cross-dock')
        ui.vars['visit_type'].set('Pickup')
        self.assertFalse(frame.winfo_manager())
        ui.vars['visit_type'].set('Other')
        self.assertEqual(value.get(),'Fictional cross-dock')

    def test_missing_other_explanation_blocks_submission(self):
        from unittest.mock import patch
        ui=OperatorUI(self.root)
        ui.vars['visit_type'].set('Other')
        with patch('operator_ui.messagebox.showerror') as error, patch('operator_ui.messagebox.askyesno') as confirm:
            ui.add()
        error.assert_called_once()
        confirm.assert_not_called()
        self.assertEqual(ui.session.visits,[])

    def test_other_explanations_structured_in_visit(self):
        form=dict(DEFAULTS,visit_type='Other',source='Other',visit_type_other_explanation='Yard move',source_other_explanation='Radio report')
        row=make_visit(form,1)
        self.assertEqual(row['other_explanations'],{'visit_type':'Yard move','source':'Radio report'})

    def test_popup_outside_click_closes_and_inside_does_not(self):
        picker=DatePicker(self.root,'2026-10-15')
        picker.grid(row=5,column=0)
        picker.open_calendar()
        popup=picker.popup
        class Event: pass
        e=Event();e.widget=popup.days
        popup._outside_click(e)
        self.assertTrue(popup.winfo_exists())
        e.widget=self.root
        popup._outside_click(e)
        self.assertFalse(popup.winfo_exists())
        picker.destroy()

    def test_calendar_navigation_survives_outside_click_handler(self):
        picker=DatePicker(self.root,'2026-12-25')
        picker.open_calendar()
        picker.popup._move(1)
        self.assertEqual((picker.popup.year,picker.popup.month),(2027,1))
        picker.popup._choose(3)
        self.assertEqual(picker.get(),'2027-01-03')
        picker.destroy()

    def test_time_selector_has_readable_width_and_independent_values(self):
        picker=DateTimePicker(self.root,'2026-10-15T23:45:00')
        self.assertGreaterEqual(int(picker.period_widget.cget('width')),5)
        self.assertEqual(picker.get(),'2026-10-15T23:45:00')
        picker.destroy()

if __name__=='__main__': unittest.main()
