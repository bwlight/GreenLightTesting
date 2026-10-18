# Green Light Operator Interface V0.3 — Persistent Driver Stopwatch

## Scope
Added a separate **Driver stopwatch** tab to the accepted V0.2.2 Tkinter application. The approved `facility.py` engine is byte-for-byte unchanged. Existing calendar, manual form, and conditional Other fields are unchanged.

## Minimal policies
1. **Timestamp:** One-tap capture uses the device's local aware ISO timestamp, including the UTC offset, with whole-second precision. No facility IANA timezone is inferred. Cross-offset comparisons use UTC instants. Clock accuracy depends on the device; clock manipulation is not detectable by this offline build.
2. **Persistence:** Standard-library SQLite (`local_data/synthetic_stopwatch.sqlite3`), synchronous FULL and WAL, transactional writes. One unfinished visit at a time. Restart reopens the unfinished visit; the timer is recomputed from timestamps, not from in-memory seconds. Database files remain in the extracted folder. Back up the folder to retain test records.
3. **Corrections:** An event cannot be captured twice. Corrections require a reason and a full ISO timestamp with offset, retain the immutable original captured time, record prior/new effective times and audit time, and cannot violate event ordering. The engine uses effective timestamps. No event deletion is provided.

## Interface
- Open **4 Driver stopwatch** tab.
- Enter a fictional facility code and select visit type; click **Capture gate arrival / Start visit**.
- Click **Capture accepted check-in** and then **Capture physical exit** when appropriate.
- HH:MM display updates once a second and survives restart through the saved timestamps.
- Choose event under **Correct recorded event**, then **Correct timestamp (audited)** and provide an ISO timestamp and reason.
- **View correction history** shows original and corrected values.
- Engine-derived quality, warnings and dwell are shown below captured events.

## Verification
`xvfb-run -a python -m unittest discover -s tests -q`: **98 tests passed**, including **15 new stopwatch tests** and all prior **83** tests. Test cases cover capture, second-level precision, midnight crossing, restart, durability, duplicate prevention, ordering, multiple visits, UTC offset comparison, corrections and audit trail, and engine delegation.

## Limits
- Synthetic evaluation only. Do not enter actual driver, trip or facility data.
- The manual-entry session remains in-memory; only the stopwatch's fictional events persist.
- A completed stopwatch visit is preserved in SQLite but this minimal tab focuses on the active/recovered visit, not a history browser. Correction of completed records via the UI is not offered after a restart (records remain in the database).
- Manual corrections use ISO timestamps with offsets rather than a calendar editor; this is intentionally narrow.
- Python 3.10+ with Tkinter required; Windows physical-display evaluation pending.
- No Amazon, Hive, dispatch, network, cloud or production capability.
