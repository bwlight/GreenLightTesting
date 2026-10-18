"""Run unchanged regression suite with bundled IANA time-zone data."""
import os
from pathlib import Path
import unittest
from zoneinfo import reset_tzpath, ZoneInfo

zone_dir = Path(__file__).resolve().parent / 'vendor' / 'zoneinfo'
os.environ['PYTHONTZPATH'] = str(zone_dir)
reset_tzpath()
try:
    ZoneInfo('America/New_York')
    ZoneInfo('America/Chicago')
except Exception as exc:
    raise SystemExit(f'Bundled timezone data unavailable: {exc}')

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent / 'tests'))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
