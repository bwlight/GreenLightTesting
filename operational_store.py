"""D0.1 operational records. No synthetic records are written to this database."""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from facility import assess

FIELDS = ('facility_code','city_state','visit_type','visit_date','trip_ref','trailer_context','appointment','arrival','check_in','exit','verified','delay_cause','delay_notes','source','time_zone','duration_seconds','duration_precision','duration_source','visit_status')
TIMES = ('appointment','arrival','check_in','exit')

def data_path():
    base = os.environ.get('LOCALAPPDATA') if os.name == 'nt' else os.environ.get('XDG_DATA_HOME') or str(Path.home()/'.local'/'share')
    if not base:
        base = str(Path.home()/'AppData'/'Local')
    return Path(base)/'GreenLight'/'FacilityIntelligence'/'operational_visits.sqlite3'

def validate(row):
    row = {k: ('' if row.get(k) is None else str(row.get(k)).strip()) for k in FIELDS}
    if not row['facility_code']:
        raise ValueError('Facility code is required; use an observed code, not a guessed one.')
    if row['visit_type'] not in ('Pickup','Drop-off','Other','Unknown'):
        raise ValueError('Select a visit type (Unknown is allowed).')
    if row['visit_type']=='Other' and not row.get('visit_type_other_explanation',''):
        # Explanation is checked by UI; unknown type is supported.
        pass
    if row['visit_status'] not in ('Incomplete','Completed'):
        raise ValueError('Choose Incomplete or Completed.')
    parsed=[]
    for k in TIMES:
        value=row[k]
        if value:
            try: t=datetime.fromisoformat(value)
            except ValueError: raise ValueError(f'{k}: use ISO timestamp with seconds, or leave blank.')
            if t.tzinfo is None or t.utcoffset() is None:
                raise ValueError(f'{k}: include explicit UTC offset, e.g. 2026-10-12T10:20:00-05:00; never assume facility timezone.')
            if t.microsecond:
                raise ValueError(f'{k}: timestamps must have whole-second precision.')
            parsed.append((k,t.astimezone(timezone.utc)))
    site=[(k,t) for k,t in parsed if k in ('arrival','check_in','exit')]
    if any(b[1]<a[1] for a,b in zip(site,site[1:])):
        raise ValueError('Site events must be chronological (arrival, check-in, exit).')
    if row['duration_seconds']:
        try: seconds=int(row['duration_seconds'])
        except ValueError: raise ValueError('Duration must be a whole number of seconds.')
        if seconds<0: raise ValueError('Duration cannot be negative.')
        if row['duration_precision'] not in ('seconds','minutes','approximate'):
            raise ValueError('Choose duration precision.')
        if not row['duration_source']:
            raise ValueError('Specify how the duration was observed.')
    else:
        if row['duration_precision'] or row['duration_source']:
            raise ValueError('Duration precision/source require a duration value.')
    if row['visit_status']=='Completed' and not (row['exit'] or row['duration_seconds']):
        raise ValueError('Completed records need physical exit or observed duration; otherwise select Incomplete.')
    return row

class OperationalStore:
    def __init__(self,path=None):
        self.path=Path(path) if path is not None else data_path()
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(str(self.path),timeout=15)
        self.db.execute('PRAGMA busy_timeout=15000')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS visits(id TEXT PRIMARY KEY, schema_version INTEGER NOT NULL, record_json TEXT NOT NULL, created_utc TEXT NOT NULL, updated_utc TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS revisions(id INTEGER PRIMARY KEY AUTOINCREMENT, visit_id TEXT NOT NULL REFERENCES visits(id), changed_utc TEXT NOT NULL, reason TEXT NOT NULL, before_json TEXT, after_json TEXT NOT NULL);
        ''')
        self.db.commit()
    def create(self,record):
        row=validate(record)
        ident=str(uuid.uuid4()); now=datetime.now(timezone.utc).isoformat(timespec='seconds')
        payload=json.dumps(row,sort_keys=True)
        with self.db:
            self.db.execute('INSERT INTO visits VALUES(?,?,?,?,?)',(ident,1,payload,now,now))
            self.db.execute('INSERT INTO revisions(visit_id,changed_utc,reason,before_json,after_json) VALUES(?,?,?,?,?)',(ident,now,'INITIAL_CAPTURE',None,payload))
        return ident
    def get(self,ident):
        r=self.db.execute('SELECT record_json FROM visits WHERE id=?',(ident,)).fetchone()
        if r is None: raise KeyError(ident)
        return json.loads(r[0])
    def edit(self,ident,record,reason):
        if not reason or not reason.strip(): raise ValueError('Correction reason is required.')
        row=validate(record)
        old=self.get(ident)
        if row==old: raise ValueError('No changes to save.')
        now=datetime.now(timezone.utc).isoformat(timespec='seconds')
        before=json.dumps(old,sort_keys=True); after=json.dumps(row,sort_keys=True)
        with self.db:
            self.db.execute('UPDATE visits SET record_json=?,updated_utc=? WHERE id=?',(after,now,ident))
            self.db.execute('INSERT INTO revisions(visit_id,changed_utc,reason,before_json,after_json) VALUES(?,?,?,?,?)',(ident,now,reason.strip(),before,after))
    def search(self,term='',completed_only=False):
        term=term.casefold().strip(); out=[]
        for ident,payload,updated in self.db.execute('SELECT id,record_json,updated_utc FROM visits ORDER BY updated_utc DESC,id DESC'):
            row=json.loads(payload)
            if completed_only and row['visit_status']!='Completed':continue
            if term and not any(term in str(row.get(k,'')).casefold() for k in ('facility_code','city_state','trip_ref','visit_date','delay_notes')):continue
            out.append((ident,row,updated))
        return out
    def history(self,ident):
        return [{'time':t,'reason':r,'before':json.loads(b) if b else None,'after':json.loads(a)} for t,r,b,a in self.db.execute('SELECT changed_utc,reason,before_json,after_json FROM revisions WHERE visit_id=? ORDER BY id',(ident,))]
    def metrics(self,ident):
        row=self.get(ident)
        if not all(row.get(k) for k in ('arrival','check_in','exit')):
            return {'quality':'INCOMPLETE','issues':['MISSING_SITE_TIMESTAMPS'],'total_dwell':None,'observed_duration_seconds':row.get('duration_seconds') or None}
        raw=dict(row);raw['visit_id']=ident
        raw['visit_date']=raw['visit_date'] or datetime.fromisoformat(raw['arrival']).date().isoformat()
        raw['appointment']=raw['appointment'] or None
        raw['time_zone']=raw['time_zone'] or None
        result=assess(raw)
        result['observed_duration_seconds']=row.get('duration_seconds') or None
        return result
    def close(self):self.db.close()
