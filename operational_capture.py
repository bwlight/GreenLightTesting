"""One-click operational progression; no schema changes or synthetic stopwatch coupling."""
from datetime import datetime, timezone
from operational_store import FIELDS, validate
import json

EVENTS = {'arrival':'Arrived', 'check_in':'Checked In', 'exit':'Left'}

def observed_now():
    # The offset is observed from the Windows device, NOT verified facility time.
    return datetime.now().astimezone().replace(microsecond=0)

class CaptureService:
    def __init__(self, store, clock=observed_now):
        self.store=store
        self.clock=clock

    def new_arrival(self, facility, visit_type, trailer, city_state=''):
        if not facility.strip(): raise ValueError('Enter a facility code before recording arrival.')
        if visit_type not in ('Pickup','Drop-off'): raise ValueError('Choose Pickup or Drop-off.')
        if trailer not in ('Loaded','Empty'): raise ValueError('Choose Loaded or Empty.')
        now=self.clock()
        self._check_clock(now)
        row={k:'' for k in FIELDS}
        row.update(facility_code=facility.strip(),city_state=city_state.strip(),visit_type=visit_type,
                   trailer_context=trailer,visit_date=now.date().isoformat(),arrival=now.isoformat(timespec='seconds'),
                   visit_status='Incomplete',verified='No',source='Firsthand',delay_cause='Unknown')
        ident=self.store.create(row)
        return ident,now.isoformat(timespec='seconds')

    @staticmethod
    def _check_clock(now):
        if now.tzinfo is None or now.utcoffset() is None or now.microsecond:
            raise ValueError('The computer clock must provide a whole-second time and UTC offset.')

    def capture(self, ident, event):
        if event not in ('check_in','exit'): raise ValueError('Use Arrived to begin a new visit.')
        now=self.clock();self._check_clock(now)
        with self.store.db:
            row=self.store.get(ident)
            if row[event]: raise ValueError(f'{EVENTS[event]} is already saved. Use audited corrections to change it.')
            if not row['arrival']: raise ValueError('Record arrival first.')
            if row['exit']: raise ValueError('This visit is already finished.')
            prev=datetime.fromisoformat(row['check_in'] or row['arrival'])
            if now.astimezone(timezone.utc)<prev.astimezone(timezone.utc):
                raise ValueError('Computer time is earlier than the previous event. Check the clock; nothing was overwritten.')
            offset_changed=now.utcoffset()!=prev.utcoffset()
            updated=dict(row)
            updated[event]=now.isoformat(timespec='seconds')
            if event=='exit':updated['visit_status']='Completed'
            updated=validate(updated)
            stamp=datetime.now(timezone.utc).isoformat(timespec='seconds')
            reason='EVENT_CAPTURE_'+event.upper()+'_DEVICE_OFFSET'
            if offset_changed:reason+='__OFFSET_CHANGED_REVIEW'
            before=json.dumps(row,sort_keys=True);after=json.dumps(updated,sort_keys=True)
            cur=self.store.db.execute('UPDATE visits SET record_json=?,updated_utc=? WHERE id=? AND record_json=?',
                                      (after,stamp,ident,before))
            if cur.rowcount!=1: raise ValueError('Visit changed during capture. Reload it before continuing.')
            self.store.db.execute('INSERT INTO revisions(visit_id,changed_utc,reason,before_json,after_json) VALUES(?,?,?,?,?)',
                                  (ident,stamp,reason,before,after))
        return now.isoformat(timespec='seconds'),offset_changed

    def record_delay(self,ident,choice,notes=''):
        choices={'No problems':'None','Slow check-in / understaffed':'Facility',
                 'Trailer missing / wrong location':'Equipment',
                 'Trailer information incorrect':'Equipment','Something else':'Mixed'}
        if choice not in choices:raise ValueError('Choose a delay reason.')
        with self.store.db:
            old=self.store.get(ident)
            if old.get('delay_cause') not in ('','Unknown'):
                raise ValueError('Delay information is already saved. Use audited corrections to change it.')
            updated=dict(old);updated['delay_cause']=choices[choice]
            updated['delay_notes']=(choice if choice!='No problems' else '')+((' — '+notes.strip()) if notes.strip() else '')
            updated=validate(updated)
            stamp=datetime.now(timezone.utc).isoformat(timespec='seconds')
            before=json.dumps(old,sort_keys=True);after=json.dumps(updated,sort_keys=True)
            cur=self.store.db.execute('UPDATE visits SET record_json=?,updated_utc=? WHERE id=? AND record_json=?',
                                      (after,stamp,ident,before))
            if cur.rowcount!=1:raise ValueError('Visit changed; reload before saving.')
            self.store.db.execute('INSERT INTO revisions(visit_id,changed_utc,reason,before_json,after_json) VALUES(?,?,?,?,?)',
                                  (ident,stamp,'NORMAL_DELAY_OBSERVATION',before,after))

    def unfinished(self):
        return [(ident,row) for ident,row,_ in self.store.search() if row.get('arrival') and not row.get('exit') and row.get('visit_status')=='Incomplete']
