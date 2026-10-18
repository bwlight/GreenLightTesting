"""Offline Tkinter calendar and 12-hour time controls; no calculation logic."""
import calendar
from datetime import date, datetime
import tkinter as tk
from tkinter import ttk


def date_label(iso_date):
    return date.fromisoformat(iso_date).strftime('%b %d, %Y')


def timestamp_from_parts(day, hour, minute, period):
    """Emit the engine's original naive ISO timestamp representation."""
    date.fromisoformat(day)
    h, m = int(hour), int(minute)
    if not 1 <= h <= 12 or not 0 <= m <= 59 or period not in ('AM', 'PM'):
        raise ValueError('Invalid 12-hour clock value')
    h24 = h % 12 + (12 if period == 'PM' else 0)
    return f'{day}T{h24:02d}:{m:02d}:00'


def parts_from_timestamp(value):
    """Read an ISO timestamp without changing its date or wall-clock time."""
    dt = datetime.fromisoformat(value)
    return dt.date().isoformat(), str(dt.hour % 12 or 12), f'{dt.minute:02d}', ('PM' if dt.hour >= 12 else 'AM')


def month_cells(year, month):
    return calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)


def popup_position(anchor_x, anchor_y, anchor_width, anchor_height, popup_width, popup_height,
                   screen_x, screen_y, screen_width, screen_height, gap=6):
    """Position below anchor, flip above if needed, and clamp to visible screen."""
    left, top = screen_x, screen_y
    right, bottom = left + screen_width, top + screen_height
    x = max(left, min(anchor_x, right - popup_width))
    below = anchor_y + anchor_height + gap
    above = anchor_y - gap - popup_height
    y = above if below + popup_height > bottom and above >= top else below
    y = max(top, min(y, bottom - popup_height))
    return int(x), int(y)


class CalendarPopup(tk.Toplevel):
    def __init__(self, parent, selected, on_select, anchor=None):
        super().__init__(parent)
        self.transient(parent.winfo_toplevel())
        self.title('Choose a date')
        self.resizable(False, False)
        self.selected = date.fromisoformat(selected)
        self.year, self.month = self.selected.year, self.selected.month
        self.on_select = on_select
        self._build()
        self.update_idletasks()
        anchor = anchor or parent
        # Button coordinates are in screen pixels; use the monitor's visible work area
        # when available through Tk's virtual root, otherwise screen dimensions.
        vx, vy = self.winfo_vrootx(), self.winfo_vrooty()
        vw, vh = self.winfo_vrootwidth(), self.winfo_vrootheight()
        if vw <= 1 or vh <= 1:
            vx, vy, vw, vh = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = popup_position(anchor.winfo_rootx(), anchor.winfo_rooty(),
                              anchor.winfo_width(), anchor.winfo_height(),
                              self.winfo_reqwidth(), self.winfo_reqheight(),
                              vx, vy, vw, vh)
        self.geometry(f'+{x}+{y}')
        # No grab: a grab routes outside clicks into the popup and can make
        # dismissal unreliable on Windows. Observe actual pointer targets.
        self._outside_root = parent.winfo_toplevel()
        self._outside_binding = self._outside_root.bind('<ButtonPress-1>', self._outside_click, add='+')
        self.bind('<Destroy>', self._cleanup_binding, add='+')
        self.focus_set()

    def _outside_click(self, event):
        if not self.winfo_exists():
            return
        target = event.widget
        while target is not None:
            if target == self:
                return
            target = getattr(target, 'master', None)
        self.destroy()

    def _cleanup_binding(self, event):
        if event.widget == self and getattr(self, '_outside_binding', None):
            self._outside_root.unbind('<ButtonPress-1>', self._outside_binding)
            self._outside_binding = None

    def _build(self):
        outer = ttk.Frame(self, padding=10)
        outer.pack()
        header = ttk.Frame(outer)
        header.grid(row=0, column=0, columnspan=7, sticky='ew', pady=(0, 8))
        ttk.Button(header, text='◀', width=3, command=lambda: self._move(-1)).pack(side='left')
        self.month_title = ttk.Label(header, width=21, anchor='center', font=('Segoe UI', 10, 'bold'))
        self.month_title.pack(side='left', expand=True)
        ttk.Button(header, text='▶', width=3, command=lambda: self._move(1)).pack(side='right')
        for i, day in enumerate(('Sun','Mon','Tue','Wed','Thu','Fri','Sat')):
            ttk.Label(outer, text=day, width=5, anchor='center').grid(row=1, column=i)
        self.days = ttk.Frame(outer)
        self.days.grid(row=2, column=0, columnspan=7)
        self._draw()
        self.bind('<Escape>', lambda event: self.destroy())

    def _move(self, delta):
        index = self.year * 12 + self.month - 1 + delta
        self.year, rem = divmod(index, 12)
        self.month = rem + 1
        self._draw()

    def _draw(self):
        self.month_title.config(text=f'{calendar.month_name[self.month]} {self.year}')
        for child in self.days.winfo_children():
            child.destroy()
        for r, week in enumerate(month_cells(self.year, self.month)):
            for c, number in enumerate(week):
                if number:
                    label = f'[{number}]' if date(self.year, self.month, number) == self.selected else str(number)
                    ttk.Button(self.days, text=label, width=5,
                               command=lambda n=number: self._choose(n)).grid(row=r, column=c, padx=1, pady=1)
                else:
                    ttk.Label(self.days, width=5).grid(row=r, column=c)

    def _choose(self, number):
        self.on_select(date(self.year, self.month, number).isoformat())
        self.destroy()


class DatePicker(ttk.Frame):
    def __init__(self, parent, initial):
        super().__init__(parent)
        self.value = tk.StringVar(value=initial)
        self.display = tk.StringVar(value=date_label(initial))
        self.field = ttk.Entry(self, textvariable=self.display, state='readonly', width=17)
        self.field.pack(side='left', fill='x', expand=True)
        self.field.bind('<Button-1>', self.open_calendar)
        self.button = ttk.Button(self, text='📅', width=3, command=self.open_calendar)
        self.button.pack(side='left', padx=(3,0))
        self.popup = None

    def open_calendar(self, event=None):
        if self.popup is not None and self.popup.winfo_exists():
            self.popup.lift()
            return
        self.popup = CalendarPopup(self, self.value.get(), self.set_date, anchor=self.button)

    def set_date(self, iso_date):
        self.value.set(date.fromisoformat(iso_date).isoformat())
        self.display.set(date_label(self.value.get()))

    def get(self):
        return self.value.get()


class DateTimePicker(ttk.Frame):
    def __init__(self, parent, initial, optional=False):
        super().__init__(parent)
        self.optional = optional
        self.enabled = tk.BooleanVar(value=bool(initial))
        self.date_picker = DatePicker(self, initial[:10] if initial else '2026-10-15')
        self.date_picker.pack(side='left', padx=(0,5))
        day, hour, minute, period = parts_from_timestamp(initial) if initial else ('2026-10-15','12','00','PM')
        self.hour = tk.StringVar(value=hour)
        self.minute = tk.StringVar(value=minute)
        self.period = tk.StringVar(value=period)
        self.hour_widget = ttk.Spinbox(self, from_=1, to=12, wrap=True, textvariable=self.hour, width=3, justify='center')
        self.hour_widget.pack(side='left', padx=(2,3))
        ttk.Label(self, text=':').pack(side='left')
        self.minute_widget = ttk.Spinbox(self, from_=0, to=59, wrap=True, format='%02.0f', textvariable=self.minute, width=3, justify='center')
        self.minute_widget.pack(side='left', padx=(3,2))
        self.period_widget = ttk.Combobox(self, textvariable=self.period, values=('AM','PM'), width=5, state='readonly', justify='center')
        self.period_widget.pack(side='left', padx=(8,5))
        if optional:
            self.none_widget = ttk.Checkbutton(self, text='No appointment', variable=self.enabled,
                                               onvalue=False, offvalue=True, command=self._toggle)
            self.none_widget.pack(side='left', padx=(8,0))
            self._toggle()

    def _toggle(self):
        state = 'normal' if self.enabled.get() else 'disabled'
        self.date_picker.field.configure(state='readonly' if self.enabled.get() else 'disabled')
        self.date_picker.button.configure(state=state)
        self.hour_widget.configure(state=state)
        self.minute_widget.configure(state=state)
        self.period_widget.configure(state='readonly' if self.enabled.get() else 'disabled')

    def get(self):
        if self.optional and not self.enabled.get():
            return ''
        return timestamp_from_parts(self.date_picker.get(), self.hour.get(), self.minute.get(), self.period.get())
