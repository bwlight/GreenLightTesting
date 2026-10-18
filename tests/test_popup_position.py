import unittest
from date_controls import popup_position, DatePicker
import tkinter as tk

class PopupPositionTests(unittest.TestCase):
    def test_below_anchor_with_gap(self):
        self.assertEqual(popup_position(200,100,30,25,260,280,0,0,1920,1080),(200,131))

    def test_flip_above_when_bottom_overflows(self):
        self.assertEqual(popup_position(200,950,30,25,260,280,0,0,1920,1080),(200,664))

    def test_clamp_right_and_left(self):
        self.assertEqual(popup_position(1880,100,30,25,260,280,0,0,1920,1080),(1660,131))
        self.assertEqual(popup_position(-30,100,30,25,260,280,0,0,1920,1080),(0,131))

    def test_clamp_when_neither_above_nor_below_fits(self):
        self.assertEqual(popup_position(100,130,30,25,260,280,0,0,800,300),(100,20))

    def test_nonzero_monitor_origin(self):
        self.assertEqual(popup_position(-100,800,30,25,260,280,-1280,0,1280,900),(-260,514))

    def test_each_of_five_controls_uses_own_button_anchor(self):
        try:
            root=tk.Tk()
        except tk.TclError:
            self.skipTest('Graphical desktop unavailable')
        try:
            root.geometry('1000x700+100+100')
            pickers=[]
            for idx in range(5):
                picker=DatePicker(root,'2026-10-11')
                picker.grid(row=idx,column=0,pady=10)
                pickers.append(picker)
            root.update()
            for picker in pickers:
                picker.open_calendar()
                root.update()
                popup=picker.popup
                self.assertEqual(popup.winfo_x(),popup_position(
                    picker.button.winfo_rootx(),picker.button.winfo_rooty(),
                    picker.button.winfo_width(),picker.button.winfo_height(),
                    popup.winfo_reqwidth(),popup.winfo_reqheight(),
                    popup.winfo_vrootx(),popup.winfo_vrooty(),
                    popup.winfo_vrootwidth(),popup.winfo_vrootheight())[0])
                popup.destroy()
        finally:
            root.destroy()

if __name__=='__main__': unittest.main()
