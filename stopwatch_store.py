"""Offline, synthetic-only, durable driver event capture. No calculation logic here."""
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from facility import assess

EVENTS = ('arrival', 'check_in', 'exit')


def now_stamp():
    """Device-local aware instant, rounded to seconds; no facility zone inferred."""
    return datetime.now().astimezone().isoformat(timespec='seconds')


def validate_stamp(value):
    try:
        dt = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError('Enter an ISO timestamp with UTC offset, e.g. 2026-10-15T23:59:05-05:00') from None
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError('A UTC offset is required; a facility timezone is never assumed.')
    if dt.microsecond:
        raise ValueError('Timestamp must have whole-second precision.')
    return dt


class StopwatchStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.path), timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS visits (
          id TEXT PRIMARY KEY, facility_code TEXT NOT NULL, visit_type TEXT NOT NULL,
          appointment TEXT, started_at TEXT NOT NULL, completed_at TEXT);
        CREATE TABLE IF NOT EXISTS events (
          visit_id TEXT NOT NULL REFERENCES visits(id), kind TEXT NOT NULL,
          captured_at TEXT NOT NULL, effective_at TEXT NOT NULL,
          PRIMARY KEY (visit_id, kind));
        CREATE TABLE IF NOT EXISTS corrections (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          visit_id TEXT NOT NULL, kind TEXT NOT NULL, original_capture TEXT NOT NULL,
          prior_effective TEXT NOT NULL, new_effective TEXT NOT NULL,
          reason TEXT NOT NULL, corrected_at TEXT NOT NULL,
          FOREIGN KEY (visit_id,kind) REFERENCES events(visit_id,kind));
        CREATE UNIQUE INDEX IF NOT EXISTS one_active_visit ON visits ((1)) WHERE completed_at IS NULL;
        ''')
        self.db.commit()

    def close(self):
        self.db.close()

    def active(self):
        row = self.db.execute('SELECT * FROM visits WHERE completed_at IS NULL').fetchone()
        return dict(row) if row else None

    def visit(self, visit_id):
        row = self.db.execute('SELECT * FROM visits WHERE id=?', (visit_id,)).fetchone()
        return dict(row) if row else None

    def start(self, facility_code, visit_type='Pickup', appointment=None, stamp=None):
        if not facility_code.strip():
            raise ValueError('Enter a fictional facility code first.')
        if visit_type not in ('Pickup', 'Drop-off', 'Other'):
            raise ValueError('Invalid visit type.')
        if appointment:
            validate_stamp(appointment)
        stamp = stamp or now_stamp()
        validate_stamp(stamp)
        visit_id = 'SYN-' + uuid.uuid4().hex[:16].upper()
        try:
            with self.db:
                self.db.execute('INSERT INTO visits VALUES (?,?,?,?,?,NULL)',
                                (visit_id, facility_code.strip(), visit_type, appointment, stamp))
                self.db.execute('INSERT INTO events VALUES (?,?,?,?)', (visit_id,'arrival',stamp,stamp))
        except sqlite3.IntegrityError as exc:
            raise ValueError('An unfinished visit already exists. Resume it before starting another.') from exc
        return visit_id

    def events(self, visit_id):
        return {r['kind']: dict(r) for r in self.db.execute('SELECT * FROM events WHERE visit_id=?', (visit_id,))}

    def capture(self, visit_id, kind, stamp=None):
        if kind not in ('check_in','exit'):
            raise ValueError('Only check-in and exit can be captured after arrival.')
        stamp = stamp or now_stamp()
        dt = validate_stamp(stamp)
        with self.db:
            visit = self.visit(visit_id)
            if not visit or visit['completed_at']:
                raise ValueError('No unfinished visit to capture.')
            events = self.events(visit_id)
            required = 'arrival' if kind == 'check_in' else 'check_in'
            if required not in events:
                raise ValueError('Capture the preceding event first.')
            if kind in events:
                raise ValueError('This event was already captured. Use a correction if necessary.')
            if dt.astimezone(timezone.utc) < validate_stamp(events[required]['effective_at']).astimezone(timezone.utc):
                raise ValueError('Event cannot precede the previous effective event. Use correction if necessary.')
            self.db.execute('INSERT INTO events VALUES (?,?,?,?)', (visit_id,kind,stamp,stamp))
            if kind == 'exit':
                self.db.execute('UPDATE visits SET completed_at=? WHERE id=?', (stamp,visit_id))
        return stamp

    def correct(self, visit_id, kind, replacement, reason, corrected_at=None):
        if kind not in EVENTS:
            raise ValueError('Unknown event type.')
        if not reason or not reason.strip():
            raise ValueError('Correction reason is required.')
        new_dt = validate_stamp(replacement).astimezone(timezone.utc)
        audit_stamp = corrected_at or now_stamp()
        validate_stamp(audit_stamp)
        with self.db:
            events = self.events(visit_id)
            if kind not in events:
                raise ValueError('Cannot correct an event that was never captured.')
            idx = EVENTS.index(kind)
            for neighbor, is_before in ((EVENTS[idx-1] if idx else None, True),
                                        (EVENTS[idx+1] if idx < 2 else None, False)):
                if neighbor in events:
                    neighbor_dt = validate_stamp(events[neighbor]['effective_at']).astimezone(timezone.utc)
                    if (is_before and new_dt < neighbor_dt) or (not is_before and new_dt > neighbor_dt):
                        raise ValueError('Correction would put events out of chronological order.')
            old = events[kind]
            self.db.execute('''INSERT INTO corrections
              (visit_id,kind,original_capture,prior_effective,new_effective,reason,corrected_at)
              VALUES (?,?,?,?,?,?,?)''',
              (visit_id,kind,old['captured_at'],old['effective_at'],replacement,reason.strip(),audit_stamp))
            self.db.execute('UPDATE events SET effective_at=? WHERE visit_id=? AND kind=?',
                            (replacement,visit_id,kind))
            if kind == 'exit':
                self.db.execute('UPDATE visits SET completed_at=? WHERE id=?', (replacement,visit_id))
        return replacement

    def history(self, visit_id):
        return [dict(r) for r in self.db.execute('SELECT * FROM corrections WHERE visit_id=? ORDER BY id', (visit_id,))]

    def assessed(self, visit_id):
        """Feed unchanged approved calculation engine, using effective event instants."""
        visit = self.visit(visit_id)
        if not visit:
            raise ValueError('Unknown visit.')
        ev = self.events(visit_id)
        arrival = ev.get('arrival',{}).get('effective_at')
        arrival_dt = validate_stamp(arrival) if arrival else None
        row = dict(visit_id=visit_id, facility_code=visit['facility_code'],
                   visit_type=visit['visit_type'], visit_date=arrival_dt.date().isoformat() if arrival_dt else '',
                   verified='Yes', delay_cause='None', appointment=visit['appointment'],
                   arrival=arrival, check_in=ev.get('check_in',{}).get('effective_at'),
                   exit=ev.get('exit',{}).get('effective_at'), time_zone=None)
        return assess(row)
