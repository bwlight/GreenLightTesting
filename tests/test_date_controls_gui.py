"""Run with xvfb-run on headless Linux; on Windows uses the regular desktop."""
import tkinter as tk
import unittest
from date_controls import DatePicker, DateTimePicker

class DateControlGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root=tk.Tk(); cls.root.withdraw()
        except tk.TclError:
            raise unittest.SkipTest('Graphical desktop unavailable')

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,'root'): cls.root.destroy()

    def test_calendar_opens_on_selected_date(self):
        picker=DatePicker(self.root,'2026-12-24')
        picker.open_calendar()
        self.assertEqual((picker.popup.year,picker.popup.month,picker.popup.selected.day),(2026,12,24))
        picker.popup._choose(27)
        self.assertEqual(picker.get(),'2026-12-27')
        picker.destroy()

    def test_independent_dates_and_times(self):
        arrival=DateTimePicker(self.root,'2026-10-15T23:30:00')
        exit_time=DateTimePicker(self.root,'2026-10-16T01:15:00')
        arrival.date_picker.set_date('2026-10-17')
        self.assertEqual(exit_time.get(),'2026-10-16T01:15:00')
        self.assertEqual(arrival.get(),'2026-10-17T23:30:00')
        arrival.destroy();exit_time.destroy()

    def test_no_appointment_toggle_preserves_values(self):
        widget=DateTimePicker(self.root,'2026-10-15T10:30:00',optional=True)
        self.assertEqual(widget.get(),'2026-10-15T10:30:00')
        widget.enabled.set(False);widget._toggle()
        self.assertEqual(widget.get(),'')
        widget.enabled.set(True);widget._toggle()
        self.assertEqual(widget.get(),'2026-10-15T10:30:00')
        widget.destroy()

    def test_calendar_month_navigation(self):
        widget=DatePicker(self.root,'2026-12-24')
        widget.open_calendar();widget.popup._move(1)
        self.assertEqual((widget.popup.year,widget.popup.month),(2027,1))
        widget.popup.destroy();widget.destroy()

if __name__=='__main__':unittest.main()
