"""Run with: python run_demo.py"""
import json
from pathlib import Path
from facility import analyze

visits = json.loads((Path(__file__).parent / 'fixtures/reference_visits.json').read_text())
records, summaries = analyze(visits)
print('GREEN LIGHT — OFFLINE SYNTHETIC DEMO (no live data)')
for record in records:
    print(record['source']['visit_id'], record['quality'], 'dwell:', record['total_dwell'],
          'appointment eligible:', record['appointment_eligible'], 'warnings:', record['warnings'])
for key, summary in summaries.items():
    print('FACILITY', key, 'visits:', summary['valid_visits'],
          'mean dwell:', summary['mean_dwell'], 'appointment eligible:', summary['appointment_eligible_visits'],
          'post-appointment mean:', summary['mean_post_appointment_dwell'])
