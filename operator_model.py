"""Presentation adapter: no calculation rules; delegates to frozen M1 engine."""
import json
from pathlib import Path
from facility import analyze

FIELDS = ('visit_date','trip_ref','facility_code','city_state','visit_type',
          'trailer_context','appointment','arrival','check_in','exit',
          'verified','delay_cause','delay_notes','source','time_zone')


def make_visit(form, sequence):
    """Create synthetic-only record; identity unique within this in-memory session."""
    record = {key: str(form.get(key, '')).strip() for key in FIELDS}
    record['other_explanations'] = {key: str(form.get(key + '_other_explanation', '')).strip() for key in ('visit_type', 'source') if record.get(key) == 'Other'}
    record['visit_id'] = 'UI-SYN-%04d' % sequence
    record['appointment'] = record['appointment'] or None
    record['time_zone'] = record['time_zone'] or None
    return record


class Session:
    def __init__(self):
        self.visits = []
        self.sequence = 0

    def add(self, form):
        self.sequence += 1
        row = make_visit(form, self.sequence)
        self.visits.append(row)
        return self.results()

    def results(self):
        return analyze(self.visits)

    def clear(self):
        self.visits.clear()
        self.sequence = 0

    def load_examples(self, path):
        """Only bundled fictional examples; no general-purpose import interface."""
        with Path(path).open(encoding='utf-8') as f:
            examples = json.load(f)
        self.clear()
        for item in examples:
            self.add(item)
        return self.results()
