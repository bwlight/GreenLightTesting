"""Operational manual entry and audited history, isolated from synthetic session."""
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from operational_store import OperationalStore, FIELDS
from operational_capture import CaptureService

LABELS={'facility_code':'Facility code (observed)','city_state':'City / state (if known)','visit_type':'Visit type','visit_date':'Visit date (YYYY-MM-DD)','trip_ref':'Trip reference (optional)','trailer_context':'Trailer context','appointment':'Appointment ISO + offset','arrival':'Gate arrival ISO + offset','check_in':'Accepted check-in ISO + offset','exit':'Physical exit ISO + offset','verified':'Verified?','delay_cause':'Delay cause','delay_notes':'Observation notes','source':'Observation source','time_zone':'Facility IANA zone (only if verified)','duration_seconds':'Observed duration (seconds)','duration_precision':'Duration precision','duration_source':'Duration source','visit_status':'Visit status'}
OPTIONS={'visit_type':('Unknown','Pickup','Drop-off','Other'),'visit_status':('Incomplete','Completed'),'duration_precision':('','seconds','minutes','approximate'),'verified':('No','Yes'),'trailer_context':('Unknown','Loaded','Empty','Bobtail'),'delay_cause':('Unknown','None','Facility','Driver','Equipment','Traffic','Weather','Mixed'),'source':('','Firsthand','Driver report','Other')}
class OperationalPanel(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.store=OperationalStore();self.capture_service=CaptureService(self.store);self.active_visit=None;self.current=None;self.vars={}
        self.columnconfigure(0,weight=1);self.rowconfigure(2,weight=1)
        ttk.Label(self,text='OPERATIONAL RECORDS  •  Local SQLite  •  Saved outside the application folder  •  No cloud sync',wraplength=920).grid(row=0,column=0,sticky='w',padx=8,pady=5)
        quick=ttk.LabelFrame(self,text='Record a facility visit — OPERATIONAL (saved locally)')
        quick.grid(row=1,column=0,sticky='ew',padx=8,pady=5)
        self.quick_facility=tk.StringVar();self.quick_type=tk.StringVar(value='Pickup');self.quick_trailer=tk.StringVar(value='Loaded')
        ttk.Label(quick,text='Facility code').grid(row=0,column=0,sticky='w',padx=5)
        ttk.Entry(quick,textvariable=self.quick_facility,width=19).grid(row=0,column=1,sticky='w',padx=5)
        ttk.Label(quick,text='Visit').grid(row=0,column=2,sticky='w')
        ttk.Combobox(quick,textvariable=self.quick_type,values=('Pickup','Drop-off'),state='readonly',width=11).grid(row=0,column=3,padx=5)
        ttk.Label(quick,text='Trailer').grid(row=0,column=4,sticky='w')
        ttk.Combobox(quick,textvariable=self.quick_trailer,values=('Loaded','Empty'),state='readonly',width=9).grid(row=0,column=5,padx=5)
        self.capture_buttons={}
        for col,key,title in ((0,'arrival','Arrived'),(1,'check_in','Checked In'),(2,'exit','Left')):
            button=ttk.Button(quick,text=title,command=lambda event=key:self.capture_event(event))
            button.grid(row=1,column=col*2,columnspan=2,sticky='ew',padx=5,pady=8)
            self.capture_buttons[key]=button
        self.capture_status=tk.StringVar(value='Ready. Arrived starts a new operational visit. Device clock is not independently verified.')
        ttk.Label(quick,textvariable=self.capture_status,wraplength=850).grid(row=2,column=0,columnspan=6,sticky='w',padx=5,pady=4)
        ttk.Button(quick,text='Open saved visit / corrections',command=self.open_active).grid(row=3,column=0,columnspan=3,sticky='w',padx=5,pady=3)
        ttk.Button(quick,text='Resume unfinished visit',command=self.resume).grid(row=3,column=3,columnspan=3,sticky='w',padx=5,pady=3)
        delay=ttk.Frame(quick);delay.grid(row=4,column=0,columnspan=6,sticky='ew',padx=5,pady=3)
        ttk.Label(delay,text='Did anything slow you down? (optional)').pack(side='left')
        self.delay_choice=tk.StringVar(value='No problems')
        ttk.Combobox(delay,textvariable=self.delay_choice,state='readonly',width=24,
                     values=('No problems','Slow check-in / understaffed','Trailer missing / wrong location','Trailer information incorrect','Something else')).pack(side='left',padx=5)
        self.delay_notes=tk.StringVar()
        ttk.Entry(delay,textvariable=self.delay_notes,width=16).pack(side='left',padx=5)
        ttk.Button(delay,text='Save delay details',command=self.save_delay).pack(side='left',padx=5)
        pane=ttk.Panedwindow(self,orient='horizontal');pane.grid(row=2,column=0,sticky='nsew',padx=6,pady=4)
        left=ttk.Frame(pane);right=ttk.Frame(pane);pane.add(left,weight=3);pane.add(right,weight=2)
        actions=ttk.Frame(left);actions.pack(side='bottom',fill='x')
        ttk.Button(actions,text='Save new visit',command=self.save_new).pack(side='left',padx=2)
        ttk.Button(actions,text='Save audited correction',command=self.correct).pack(side='left',padx=2)
        ttk.Button(actions,text='New / clear form',command=self.clear).pack(side='left',padx=2)
        region=ttk.Frame(left);region.pack(fill='both',expand=True)
        canvas=tk.Canvas(region,highlightthickness=0);bar=ttk.Scrollbar(region,orient='vertical',command=canvas.yview);canvas.configure(yscrollcommand=bar.set)
        bar.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True)
        form=ttk.Frame(canvas);window=canvas.create_window((0,0),window=form,anchor='nw')
        form.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>',lambda e:canvas.itemconfigure(window,width=e.width))
        for i,key in enumerate(FIELDS):
            ttk.Label(form,text=LABELS[key]).grid(row=i,column=0,sticky='w',padx=6,pady=3)
            default={'visit_type':'Unknown','visit_status':'Incomplete','verified':'No','trailer_context':'Unknown','delay_cause':'Unknown'}.get(key,'')
            var=tk.StringVar(value=default);self.vars[key]=var
            widget=ttk.Combobox(form,textvariable=var,values=OPTIONS[key],state='readonly') if key in OPTIONS else ttk.Entry(form,textvariable=var)
            widget.grid(row=i,column=1,sticky='ew',padx=6,pady=3)
        form.columnconfigure(1,weight=1)
        ttk.Label(form,text='Timestamp example: 2026-10-12T08:15:03-05:00. Blank = unknown.\nDuration-only: enter seconds, precision, source; leave unknown times blank.',wraplength=440).grid(row=len(FIELDS),column=0,columnspan=2,sticky='w',padx=6,pady=8)
        searchrow=ttk.Frame(right);searchrow.pack(fill='x')
        self.search_var=tk.StringVar();ttk.Entry(searchrow,textvariable=self.search_var).pack(side='left',fill='x',expand=True)
        ttk.Button(searchrow,text='Search',command=self.refresh).pack(side='left')
        ttk.Button(searchrow,text='Completed',command=lambda:self.refresh(True)).pack(side='left')
        self.tree=ttk.Treeview(right,columns=('facility','status','date'),show='headings',height=9)
        for key in ('facility','status','date'):self.tree.heading(key,text=key.title());self.tree.column(key,width=110)
        self.tree.pack(fill='both',expand=True)
        self.tree.bind('<<TreeviewSelect>>',self.load)
        self.detail=tk.Text(right,height=12,wrap='word');self.detail.pack(fill='both',expand=True)
        self.status=tk.StringVar(value=f'Operational database: {self.store.path}')
        ttk.Label(self,textvariable=self.status,wraplength=950).grid(row=3,column=0,sticky='w',padx=8)
        self.refresh()
        self.resume(silent=True)
    def capture_event(self,event):
        try:
            if event=='arrival':
                if self.active_visit and not self.store.get(self.active_visit).get('exit'):
                    raise ValueError('An unfinished visit is active. Finish or correct it before starting another.')
                ident,stamp=self.capture_service.new_arrival(self.quick_facility.get(),self.quick_type.get(),self.quick_trailer.get())
                self.active_visit=ident;changed=False
            else:
                if not self.active_visit:raise ValueError('Record arrival or resume an unfinished visit first.')
                stamp,changed=self.capture_service.capture(self.active_visit,event)
            self.capture_status.set('SAVED to operational SQLite — '+event.replace('_',' ').title()+' at '+stamp+' (device-observed offset; clock not independently verified)'+(' — OFFSET CHANGED: REVIEW CLOCK' if changed else ''))
            self.refresh()
        except (ValueError,OSError) as exc:
            self.capture_status.set('NOT SAVED: '+str(exc))
            messagebox.showwarning('Visit not saved',str(exc),parent=self)
    def save_delay(self):
        if not self.active_visit:
            self.capture_status.set('Record or resume a visit before saving delay details.');return
        try:
            self.capture_service.record_delay(self.active_visit,self.delay_choice.get(),self.delay_notes.get())
            self.capture_status.set('SAVED optional delay information to operational SQLite.')
            self.refresh()
        except (ValueError,OSError) as exc:
            self.capture_status.set('NOT SAVED: '+str(exc))
            messagebox.showwarning('Delay not saved',str(exc),parent=self)
    def resume(self,silent=False):
        pending=self.capture_service.unfinished()
        if len(pending)==1:
            self.active_visit=pending[0][0];self.quick_facility.set(pending[0][1]['facility_code'])
            self.quick_type.set(pending[0][1]['visit_type']);self.quick_trailer.set(pending[0][1]['trailer_context'])
            self.capture_status.set('Recovered unfinished operational visit: '+self.quick_facility.get())
        elif not silent:
            self.capture_status.set('No unique unfinished visit. Select the correct record in visit history.')
    def open_active(self):
        if not self.active_visit:return
        self.current=self.active_visit
        row=self.store.get(self.current)
        for k,v in self.vars.items():v.set(row.get(k,''))
        self.show_detail(self.current)
        self.status.set('Loaded for audited correction: '+self.current)
    def form(self):return {k:v.get() for k,v in self.vars.items()}
    def save_new(self):
        try:
            ident=self.store.create(self.form());self.current=ident;self.refresh();self.status.set('SAVED to operational SQLite: '+ident)
        except (ValueError,OSError) as e:messagebox.showerror('Not saved',str(e))
    def correct(self):
        if not self.current:messagebox.showwarning('Select visit','Select a saved visit to correct.');return
        reason=simpledialog.askstring('Correction reason','Reason for changing the original observation:',parent=self)
        if reason is None:return
        try:
            self.store.edit(self.current,self.form(),reason);self.refresh();self.show_detail(self.current);self.status.set('AUDITED CORRECTION SAVED: '+self.current)
        except (ValueError,OSError) as e:messagebox.showerror('Not saved',str(e))
    def clear(self):
        self.current=None
        for k,v in self.vars.items():v.set({'visit_type':'Unknown','visit_status':'Incomplete','verified':'No','trailer_context':'Unknown','delay_cause':'Unknown'}.get(k,''))
        self.status.set('New operational visit; not yet saved.')
    def refresh(self,completed_only=False):
        for item in self.tree.get_children():self.tree.delete(item)
        for ident,row,updated in self.store.search(self.search_var.get(),completed_only):
            self.tree.insert('','end',iid=ident,values=(row['facility_code'],row['visit_status'],row['visit_date']))
    def load(self,event=None):
        selection=self.tree.selection()
        if not selection:return
        self.current=selection[0]
        row=self.store.get(self.current)
        for k,v in self.vars.items():v.set(row.get(k,''))
        self.show_detail(self.current)
        self.status.set('Retrieved saved operational visit: '+self.current)
    def show_detail(self,ident):
        m=self.store.metrics(ident);hist=self.store.history(ident)
        lines=['Record ID: '+ident,'Quality: '+m['quality'],'Total dwell (approved engine): '+str(m.get('total_dwell') or 'Not available'),'Observed duration seconds (separate measurement): '+str(m.get('observed_duration_seconds') or 'Not available'),'Issues: '+str(m.get('issues',[])),'','AUDIT HISTORY (old and new values preserved):']
        for h in hist:lines.extend([h['time']+' — '+h['reason'],'Before: '+json.dumps(h['before'],sort_keys=True),'After: '+json.dumps(h['after'],sort_keys=True),''])
        self.detail.delete('1.0','end');self.detail.insert('1.0','\n'.join(lines))
    def shutdown(self):self.store.close()
