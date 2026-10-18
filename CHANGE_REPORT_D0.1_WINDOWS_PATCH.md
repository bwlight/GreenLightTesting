# D0.1 Windows corrective patch

## Diagnosis
The five reported failures all rely on IANA timezone data. Windows Python installations may not have this data for `zoneinfo`; missing data triggers the engine's existing INVALID_TIME_ZONE branch. The batch launcher and test runner now point `PYTHONTZPATH` at bundled IANA TZif data in `vendor/zoneinfo`. The existing calculation engine and its five original tests remain unchanged. Bundled timezone data licensing is included.

The Tkinter stopwatch recurring `after` callback was not cancelled on shutdown. The patch tracks and cancels its scheduled callback, and prevents rescheduling during shutdown. Calendar code is unchanged.

## Verification
110/110 tests passed under Linux virtual display, including the five previously failed tests and two new regression tests. This is not a substitute for founder Windows testing. Approved calculation engine SHA-256: `6deb0b5a0c1b539b60286e8195f8359d896c30dc17dcadc91bfd6c0268a502de` (unchanged). No operational SQLite schema, location, or migration changed.

## Targeted Windows retest
1. Extract patch to a new folder; do not touch existing Windows user-data folder.
2. Double-click `Run_Tests.bat`; expect 110 tests, 0 failures, 0 skipped. Check five previously failed tests are `ok`.
3. Launch app, open synthetic stopwatch, start a fictional visit, close/reopen several times; confirm no `invalid command name ... tick` warnings.
4. Open operational visit history; retrieve an existing visit and its audit history.
5. Confirm test run works without network or installing Python packages.

## UI backlog plan (separate increments)
A. UI-004 operational-first navigation, UI-001 plain-English controls and H/M/S duration entry, UI-005 required-field indicators and operator guide.
B. UI-002 live Windows clock with capture/freeze, UI-003 wheel follows hovered panel.
C. UI-006 readable audit history, UI-007 actionable validation messages.
Founder-test each increment. Complete all seven before R1.0; D0.2 directory and D0.3 export/backup/recovery remain separate mandatory gates.

No D0.2, D0.3, Hive, cloud, dispatch or mobile features added.
