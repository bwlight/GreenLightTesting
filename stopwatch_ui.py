"""Tkinter controls for durable synthetic stopwatch; no calculation rules."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timezone
from stopwatch_store import StopwatchStore, now_stamp


class StopwatchPanel(ttk.Frame):
    def __init__(self, parent, database_path):
        super().__init__(parent)
        self.store = StopwatchStore(database_path)
        self.current_id = None
        self._tick_job = None
        self._shutting_down = False
        self.code = tk.StringVar(value='SYN-FACILITY')
        self.kind = tk.StringVar(value='Pickup')
        self.status = tk.StringVar()
        self.elapsed = tk.StringVar(value='00:00')
        self.details = tk.StringVar()
        header = ttk.Frame(self); header.pack(fill='x', padx=14, pady=10)
        ttk.Label(header, text='FICTIONAL DRIVER STOPWATCH  |  Stored locally; no live facility data',style='Warning.TLabel').pack(anchor='w')
        setup = ttk.Frame(self); setup.pack(fill='x',padx=14,pady=4)
        ttk.Label(setup,text='Fictional facility code').pack(side='left',padx=(0,5))
        ttk.Entry(setup,textvariable=self.code,width=22).pack(side='left',padx=5)
        ttk.Label(setup,text='Visit type').pack(side='left',padx=5)
        ttk.Combobox(setup,textvariable=self.kind,values=('Pickup','Drop-off','Other'),state='readonly',width=12).pack(side='left')
        self.start_button = ttk.Button(setup,text='Capture gate arrival / Start visit',style='Primary.TButton',command=self.start)
        self.start_button.pack(side='left',padx=10)
        ttk.Label(self,textvariable=self.elapsed,font=('Segoe UI',32,'bold')).pack(pady=(8,0))
        ttk.Label(self,text='LIVE ELAPSED  HH:MM  •  source timestamps saved to the second').pack()
        actions=ttk.Frame(self);actions.pack(pady=12)
        self.check_button=ttk.Button(actions,text='Capture accepted check-in',command=lambda:self.capture('check_in'))
        self.check_button.pack(side='left',padx=8)
        self.exit_button=ttk.Button(actions,text='Capture physical exit',command=lambda:self.capture('exit'),style='Primary.TButton')
        self.exit_button.pack(side='left',padx=8)
        ttk.Label(self,textvariable=self.status,wraplength=850).pack(fill='x',padx=14,pady=6)
        ttk.Label(self,textvariable=self.details,justify='left',wraplength=900).pack(fill='x',padx=14,pady=5)
        correction=ttk.Frame(self);correction.pack(fill='x',padx=14,pady=8)
        ttk.Label(correction,text='Correct recorded event:').pack(side='left')
        self.correct_kind=tk.StringVar(value='arrival')
        ttk.Combobox(correction,textvariable=self.correct_kind,values=('arrival','check_in','exit'),state='readonly',width=13).pack(side='left',padx=8)
        ttk.Button(correction,text='Correct timestamp (audited)',command=self.correct).pack(side='left')
        ttk.Button(correction,text='View correction history',command=self.history).pack(side='left',padx=8)
        self.current_id = (self.store.active() or {}).get('id')
        self.refresh()
        self._tick_job = self.after(1000,self.tick)

    def start(self):
        try:
            self.current_id=self.store.start(self.code.get(),self.kind.get())
            self.refresh()
        except ValueError as exc: messagebox.showerror('Cannot start',str(exc),parent=self)

    def capture(self,kind):
        try:
            self.store.capture(self.current_id,kind)
            self.refresh()
        except ValueError as exc: messagebox.showerror('Cannot capture',str(exc),parent=self)

    def correct(self):
        if not self.current_id:
            messagebox.showinfo('No visit','Start a fictional visit first.',parent=self);return
        kind=self.correct_kind.get()
        ev=self.store.events(self.current_id).get(kind)
        if not ev:
            messagebox.showinfo('Not captured','Capture this event before correcting it.',parent=self);return
        stamp=simpledialog.askstring('Correct '+kind,'ISO timestamp with offset (seconds):',initialvalue=ev['effective_at'],parent=self)
        if stamp is None:return
        reason=simpledialog.askstring('Correction reason','Required reason for changing the timestamp:',parent=self)
        if reason is None:return
        try:
            self.store.correct(self.current_id,kind,stamp,reason)
            self.refresh()
        except ValueError as exc: messagebox.showerror('Correction rejected',str(exc),parent=self)

    def history(self):
        if not self.current_id:return
        rows=self.store.history(self.current_id)
        text='\n\n'.join(f"{r['kind']}: {r['prior_effective']} → {r['new_effective']}\nReason: {r['reason']}\nAudit: {r['corrected_at']}\nOriginal: {r['original_capture']}" for r in rows)
        messagebox.showinfo('Correction history',text or 'No corrections.',parent=self)

    def refresh(self):
        if not self.current_id:
            self.status.set('READY — No active visit. Capture fictional gate arrival to begin.')
            self.details.set('No captured events.')
            self.start_button.configure(state='normal')
            self.check_button.configure(state='disabled')
            self.exit_button.configure(state='disabled')
            return
        visit=self.store.visit(self.current_id)
        ev=self.store.events(self.current_id)
        complete=bool(visit['completed_at'])
        self.start_button.configure(state='disabled' if not complete else 'normal')
        self.check_button.configure(state='normal' if not complete and 'check_in' not in ev else 'disabled')
        self.exit_button.configure(state='normal' if not complete and 'check_in' in ev and 'exit' not in ev else 'disabled')
        self.status.set(('COMPLETE' if complete else 'ACTIVE / RECOVERABLE')+'  |  '+visit['facility_code']+'  |  '+self.current_id)
        assessed=self.store.assessed(self.current_id)
        times='\n'.join(f"{k.replace('_',' ').title()}: {ev[k]['effective_at']}" for k in ('arrival','check_in','exit') if k in ev)
        self.details.set(times+'\nEngine quality: '+assessed['quality']+' | Dwell: '+str(assessed['total_dwell'])+' min\nIssues: '+(', '.join(assessed['issues']) or 'None')+' | Warnings: '+(', '.join(assessed['warnings']) or 'None'))
        self.tick_display()

    def tick_display(self):
        if not self.current_id:return
        ev=self.store.events(self.current_id)
        if 'arrival' not in ev:return
        visit=self.store.visit(self.current_id)
        start=datetime.fromisoformat(ev['arrival']['effective_at']).astimezone(timezone.utc)
        end=datetime.fromisoformat(ev['exit']['effective_at']).astimezone(timezone.utc) if 'exit' in ev else datetime.now(timezone.utc)
        seconds=max(0,int((end-start).total_seconds()))
        self.elapsed.set(f'{seconds//3600:02d}:{(seconds%3600)//60:02d}')

    def tick(self):
        self._tick_job = None
        if self._shutting_down or not self.winfo_exists():
            return
        self.tick_display()
        if not self._shutting_down:
            self._tick_job = self.after(1000, self.tick)

    def shutdown(self):
        if self._shutting_down:
            return
        self._shutting_down = True
        if self._tick_job is not None:
            try:
                self.after_cancel(self._tick_job)
            except tk.TclError:
                pass
            self._tick_job = None
        self.store.close()

    def destroy(self):
        # Tk destroys child widgets during root teardown even when WM_DELETE_WINDOW
        # is not invoked (as in automated GUI tests). Cancel scheduled Tcl jobs
        # before the widget's Tcl command is deleted.
        self.shutdown()
        super().destroy()
