import unittest
from datetime import date
from date_controls import timestamp_from_parts, parts_from_timestamp, month_cells

class DateControlTests(unittest.TestCase):
    def test_noon(self): self.assertEqual(timestamp_from_parts('2026-10-15','12','00','PM'),'2026-10-15T12:00:00')
    def test_midnight(self): self.assertEqual(timestamp_from_parts('2026-10-15','12','00','AM'),'2026-10-15T00:00:00')
    def test_evening(self): self.assertEqual(timestamp_from_parts('2026-10-16','1','07','AM'),'2026-10-16T01:07:00')
    def test_roundtrip(self):
        for hour in range(24):
            value=f'2026-10-15T{hour:02d}:37:00'
            self.assertEqual(timestamp_from_parts(*parts_from_timestamp(value)),value)
    def test_invalid_hour(self):
        with self.assertRaises(ValueError): timestamp_from_parts('2026-10-15','13','00','AM')
    def test_invalid_minute(self):
        with self.assertRaises(ValueError): timestamp_from_parts('2026-10-15','11','60','AM')
    def test_invalid_date(self):
        with self.assertRaises(ValueError): timestamp_from_parts('2026-02-30','11','00','AM')
    def test_sunday_first_calendar(self):
        weeks=month_cells(2026,10)
        self.assertEqual(weeks[0][4],1)
    def test_overnight_independent_dates(self):
        a=timestamp_from_parts('2026-10-15','11','30','PM')
        b=timestamp_from_parts('2026-10-16','1','15','AM')
        self.assertEqual((__import__('datetime').datetime.fromisoformat(b)-__import__('datetime').datetime.fromisoformat(a)).total_seconds(),6300)

if __name__=='__main__': unittest.main()
