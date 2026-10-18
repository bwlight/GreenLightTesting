"""Local Tkinter evaluation interface. All computations come from facility.py."""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from operator_model import FIELDS, Session
from date_controls import DatePicker, DateTimePicker
from green_light_theme import apply_theme, CHARCOAL, PANEL, TEXT, ELECTRIC_GREEN
from stopwatch_ui import StopwatchPanel
from operational_ui import OperationalPanel

ROOT = Path(__file__).resolve().parent
DISPLAY = {
 'visit_date':'Visit date', 'trip_ref':'Fictional trip reference',
 'facility_code':'Fictional facility code', 'city_state':'Fictional city / state',
 'visit_type':'Visit type', 'trailer_context':'Trailer context',
 'appointment':'Appointment date / time', 'arrival':'Physical arrival date / time',
 'check_in':'Accepted check-in date / time', 'exit':'Physical exit date / time',
 'verified':'Verified?', 'delay_cause':'Delay cause',
 'delay_notes':'Fictional notes', 'source':'Observation source',
 'time_zone':'IANA time zone (optional)'}
CHOICES = {
 'visit_type':('Pickup','Drop-off','Other'),
 'trailer_context':('Loaded','Empty','Bobtail','Unknown'),
 'verified':('Yes','No'),
 'delay_cause':('None','Facility','Driver','Equipment','Traffic','Weather','Mixed','Unknown'),
 'source':('Firsthand','Driver report','Other')}
DEFAULTS = {
 'visit_date':'2026-10-15','trip_ref':'SYN-NEW', 'facility_code':'F-A',
 'city_state':'Fictional, ZZ','visit_type':'Pickup','trailer_context':'Loaded',
 'appointment':'2026-10-15T10:00:00', 'arrival':'2026-10-15T10:00:00',
 'check_in':'2026-10-15T10:15:00','exit':'2026-10-15T11:00:00',
 'verified':'Yes','delay_cause':'None','delay_notes':'Fictional visit only',
 'source':'Firsthand','time_zone':''}
METRICS = (
 ('arrival_vs_appointment','Arrival vs appointment'),
 ('arrival_to_check_in','Arrival to check-in'),
 ('check_in_to_exit','Check-in to exit'),
 ('total_dwell','Total site dwell'),
 ('early_arrival','Early arrival'),
 ('post_appointment_dwell','Post-appointment dwell'))


def fmt(value):
    return 'Not available' if value is None else str(value)


class OperatorUI:
    def __init__(self, root):
        self.root = root
        self.session = Session()
        root.title('Green Light | Facility Intelligence — Operator Interface D0.1')
        root.geometry('1120x790')
        root.minsize(850,620)
        root.columnconfigure(0,weight=1)
        root.rowconfigure(2,weight=1)
        ttk.Label(root,text='GREEN LIGHT  /  FACILITY INTELLIGENCE', style='Header.TLabel').grid(row=0,column=0,sticky='ew',padx=12,pady=(10,3))
        ttk.Label(root,text='OPERATIONAL VISITS: TAB 5 SAVES TO USER DATA  |  TABS 1–4 ARE SYNTHETIC / ENGINEERING ONLY  |  NO CLOUD CONNECTION.',
                  wraplength=1040, style='Warning.TLabel').grid(row=1,column=0,sticky='w',padx=12)
        body=ttk.Panedwindow(root,orient=tk.VERTICAL)
        body.grid(row=2,column=0,sticky='nsew',padx=12,pady=8)
        top=ttk.Frame(body)
        body.add(top,weight=2)
        # Pack the fixed action bar FIRST, reserving space even when the pane shrinks.
        self.action_bar=ttk.Frame(top)
        self.action_bar.pack(side='bottom',fill='x',pady=(7,3))
        # Scroll only the entry area. Keep submission actions outside this canvas.
        entry_region=ttk.Frame(top)
        entry_region.pack(fill='both',expand=True)
        self.form_canvas=tk.Canvas(entry_region,highlightthickness=0,borderwidth=0,bg=PANEL)
        self.form_scroll=ttk.Scrollbar(entry_region,orient='vertical',command=self.form_canvas.yview)
        self.form_canvas.configure(yscrollcommand=self.form_scroll.set)
        self.form_scroll.pack(side='right',fill='y')
        self.form_canvas.pack(side='left',fill='both',expand=True)
        form=ttk.LabelFrame(self.form_canvas,text='1  Fictional facility visit')
        self.form= form
        self.form_window=self.form_canvas.create_window((0,0),window=form,anchor='nw')
        form.bind('<Configure>',self._update_form_scrollregion)
        self.form_canvas.bind('<Configure>',self._resize_form_width)
        # Wheel handling is restricted to the form, so the results pane keeps its own behavior.
        form.bind('<Enter>',self._bind_form_wheel)
        form.bind('<Leave>',self._unbind_form_wheel)

        self.vars={}
        self.date_controls={}
        self.other_fields={}
        for i,key in enumerate(FIELDS):
            column=0 if i<8 else 2
            row=i if i<8 else i-8
            ttk.Label(form,text=DISPLAY[key]).grid(row=row,column=column,sticky='w',padx=(10,5),pady=4)
            v=tk.StringVar(value=DEFAULTS.get(key,''));self.vars[key]=v
            if key == 'visit_date':
                widget=DatePicker(form, DEFAULTS[key]); self.date_controls[key]=widget
            elif key in ('appointment','arrival','check_in','exit'):
                widget=DateTimePicker(form, DEFAULTS[key], optional=(key=='appointment')); self.date_controls[key]=widget
            elif key in CHOICES:
                if 'Other' in CHOICES[key]:
                    wrapper=ttk.Frame(form)
                    widget=ttk.Combobox(wrapper,textvariable=v,values=CHOICES[key],state='readonly',width=30)
                    widget.pack(fill='x')
                    note=ttk.Frame(wrapper)
                    ttk.Label(note,text='Explain Other (required):').pack(anchor='w',pady=(5,1))
                    note_var=tk.StringVar()
                    ttk.Entry(note,textvariable=note_var).pack(fill='x')
                    self.other_fields[key]=(note,note_var)
                    def toggle(*_, field=key):
                        area,_ = self.other_fields[field]
                        if self.vars[field].get() == 'Other':
                            area.pack(fill='x',pady=(0,3))
                        else:
                            area.pack_forget()
                    v.trace_add('write',toggle)
                    toggle()
                    widget=wrapper
                else:
                    widget=ttk.Combobox(form,textvariable=v,values=CHOICES[key],state='readonly',width=30)

            else:
                widget=ttk.Entry(form,textvariable=v,width=33)
            widget.grid(row=row,column=column+1,sticky='ew',padx=(0,12),pady=4)
        form.columnconfigure(1,weight=1);form.columnconfigure(3,weight=1)
        controls=self.action_bar
        ttk.Button(controls,text='Add fictional visit',command=self.add,style='Primary.TButton').pack(side='left',padx=3)
        ttk.Button(controls,text='Load 2 bundled examples',command=self.examples).pack(side='left',padx=3)
        ttk.Button(controls,text='Clear session',command=self.clear).pack(side='left',padx=3)
        ttk.Label(controls,text='Select a visit below to inspect calculations and warnings.').pack(side='right')
        lower=ttk.Notebook(body)
        body.add(lower,weight=3)
        visits_tab=ttk.Frame(lower); summary_tab=ttk.Frame(lower)
        lower.add(visits_tab,text='2  Visits and warnings')
        lower.add(summary_tab,text='3  Facility summaries')
        stopwatch_tab=ttk.Frame(lower)
        lower.add(stopwatch_tab,text='4  Driver stopwatch')
        operational_tab=ttk.Frame(lower,width=650,height=280)
        operational_tab.pack_propagate(False)
        lower.add(operational_tab,text='5  Operational visits')
        self.operational=OperationalPanel(operational_tab)
        self.operational.pack(fill='both',expand=True)
        lower.select(operational_tab)
        self.stopwatch=StopwatchPanel(stopwatch_tab,ROOT/'local_data'/'synthetic_stopwatch.sqlite3')
        self.stopwatch.pack(fill='both',expand=True)
        cols=('id','facility','type','quality','counted','dwell','appt','alerts')
        self.visits_tree=ttk.Treeview(visits_tab,columns=cols,show='headings',height=7)
        for c,title,width in [('id','Visit',110),('facility','Facility',100),('type','Type',95),('quality','Quality',85),('counted','In stats?',80),('dwell','Dwell min',95),('appt','Post-appt min',110),('alerts','Issues / warnings',300)]:
            self.visits_tree.heading(c,text=title);self.visits_tree.column(c,width=width,stretch=c=='alerts')
        self.visits_tree.pack(fill='both',expand=True)
        self.visits_tree.bind('<<TreeviewSelect>>',self.select_visit)
        self.details=tk.Text(visits_tab,height=8,wrap='word',state='disabled',font=('Consolas',10),bg=PANEL,fg=TEXT,insertbackground=ELECTRIC_GREEN,relief='flat',padx=10,pady=8)
        self.details.pack(fill='both',expand=True,pady=(6,0))
        summary_cols=('facility','type','visits','eligible','mean','post','max','delays')
        self.summary_tree=ttk.Treeview(summary_tab,columns=summary_cols,show='headings')
        for c,title,width in [('facility','Facility',140),('type','Visit type',110),('visits','Valid visits',105),('eligible','Appt eligible',110),('mean','Mean dwell min',125),('post','Mean post-appt min',150),('max','Max dwell min',125),('delays','Facility delays',110)]:
            self.summary_tree.heading(c,text=title);self.summary_tree.column(c,width=width)
        self.summary_tree.pack(fill='both',expand=True)
        self.status=tk.StringVar(value='Ready — no records. Data is in memory only.')
        ttk.Label(root,textvariable=self.status,style='Muted.TLabel').grid(row=3,column=0,sticky='ew',padx=12,pady=(0,8))

    def _update_form_scrollregion(self, event=None):
        self.form_canvas.configure(scrollregion=self.form_canvas.bbox('all'))

    def _resize_form_width(self, event):
        self.form_canvas.itemconfigure(self.form_window,width=max(1,event.width))

    def _wheel_form(self, event):
        # Tk on Windows reports 120 units per wheel notch.
        if getattr(event,'delta',0):
            self.form_canvas.yview_scroll(-int(event.delta/120) or (-1 if event.delta>0 else 1),'units')
        elif getattr(event,'num',None) in (4,5):
            self.form_canvas.yview_scroll(-1 if event.num==4 else 1,'units')

    def _bind_form_wheel(self, event=None):
        self.form_canvas.bind_all('<MouseWheel>',self._wheel_form)
        self.form_canvas.bind_all('<Button-4>',self._wheel_form)
        self.form_canvas.bind_all('<Button-5>',self._wheel_form)

    def _unbind_form_wheel(self, event=None):
        self.form_canvas.unbind_all('<MouseWheel>')
        self.form_canvas.unbind_all('<Button-4>')
        self.form_canvas.unbind_all('<Button-5>')

    def add(self):
        try:
            form={key:(self.date_controls[key].get() if key in self.date_controls else var.get()) for key,var in self.vars.items()}
        except ValueError as exc:
            messagebox.showerror('Invalid time', str(exc))
            return
        for field,(area,note_var) in self.other_fields.items():
            if form[field] == 'Other':
                explanation=note_var.get().strip()
                if not explanation:
                    messagebox.showerror('Explanation required', f'Explain Other for {DISPLAY[field]} before submitting.')
                    return
                form[field+'_other_explanation']=explanation
        if not messagebox.askyesno('Synthetic data only','Confirm these are fictional/test values only. Do not enter real driver, trip, or facility observations.'):
            return
        self.session.add(form)
        self.refresh()
        self.visits_tree.selection_set(str(len(self.session.visits)-1))
        self.select_visit()

    def examples(self):
        if self.session.visits and not messagebox.askyesno('Replace session','Replace current unsaved fictional visits with the bundled examples?'):
            return
        self.session.load_examples(ROOT/'fixtures'/'reference_visits.json')
        self.refresh()

    def clear(self):
        if self.session.visits and not messagebox.askyesno('Clear session','Discard all unsaved fictional visits?'):
            return
        self.session.clear();self.refresh()

    def refresh(self):
        results,summaries=self.session.results()
        for tree in (self.visits_tree,self.summary_tree):
            for item in tree.get_children(): tree.delete(item)
        for i,r in enumerate(results):
            raw=r['source']
            alerts=', '.join(r['issues']+r['warnings']) or 'None'
            self.visits_tree.insert('', 'end',iid=str(i),values=(raw['visit_id'],raw['facility_code'],raw['visit_type'],r['quality'],
                    'Yes' if r['counted'] else 'No',fmt(r['total_dwell']),fmt(r['post_appointment_dwell']),alerts))
        for (facility,kind),s in sorted(summaries.items()):
            self.summary_tree.insert('','end',values=(facility,kind,s['valid_visits'],s['appointment_eligible_visits'],
                fmt(s['mean_dwell']),fmt(s['mean_post_appointment_dwell']),fmt(s['max_dwell']),s['facility_coded_delays']))
        self.status.set(f'{len(results)} fictional observations  |  {sum(r["quality"]=="VALID" and r["counted"] for r in results)} included in statistics  |  Not saved to disk')
        self._set_details('Select a visit above to view the calculation details and validation messages.')

    def _set_details(self,text):
        self.details.configure(state='normal');self.details.delete('1.0','end');self.details.insert('1.0',text);self.details.configure(state='disabled')

    def select_visit(self,event=None):
        chosen=self.visits_tree.selection()
        if not chosen:return
        results,_=self.session.results();r=results[int(chosen[0])]
        lines=[f'Visit {r["source"]["visit_id"]}   |   Quality: {r["quality"]}   |   Included: {"Yes" if r["counted"] else "No"}',
               f'Appointment eligible: {"Yes" if r["appointment_eligible"] else "No"}',
               '']
        lines += [f'{label}: {fmt(r[key])} minutes' for key,label in METRICS]
        lines += [f'Other — {key}: {value}' for key,value in r['source'].get('other_explanations',{}).items()]
        lines += ['','Quality issues: '+(', '.join(r['issues']) or 'None'),
                  'Warnings: '+(', '.join(r['warnings']) or 'None'),
                  'Source observation is preserved in memory until you clear or close the program.']
        self._set_details('\n'.join(lines))


def main():
    root=tk.Tk()
    apply_theme(root)
    ui=OperatorUI(root)
    def on_close():
        ui.stopwatch.shutdown()
        ui.operational.shutdown()
        root.destroy()
    root.protocol('WM_DELETE_WINDOW',on_close)
    root.mainloop()


if __name__=='__main__':
    main()
