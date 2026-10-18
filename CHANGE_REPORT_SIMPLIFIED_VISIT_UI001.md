# Green Light — Simplified Facility Visit / UI-001 engineering test build

## Scope
- Added an operational quick-capture section inside existing Tab 5. No tab removal or reordering.
- Enter observed facility code, Pickup/Drop-off, Loaded/Empty; click Arrived, Checked In, Left.
- First event creates an incomplete operational visit. Subsequent events update the same UUID and SQLite row transactionally. Each event appends a revision with `EVENT_CAPTURE_*_DEVICE_OFFSET`, not a correction.
- An event cannot be captured twice; missing check-in does not prevent departure. Backward UTC event times are rejected.
- Captures preserve seconds and the computer's observed UTC offset. Offset changes are flagged in both the on-screen status and revision reason; this is not verification of the device clock or facility timezone.
- Optional delay selection and notes use the existing `delay_cause` and `delay_notes` fields. The specific selection is retained in notes, with a mapped existing category. Once saved, changes require the existing audited correction path.
- A unique unfinished operational visit is offered for resume at startup. If multiple unfinished visits exist, the operator must select the appropriate visit rather than silently choosing one.
- Existing manual historical entry, duration-only observations, visit history and audited corrections remain available in Tab 5. The `Open saved visit / corrections` button loads the active visit into the existing correction form.
- Existing synthetic stopwatch remains isolated and unchanged; no calendar changes.

## Preserved
- `facility.py` approved calculation engine, `operational_store.py` SQLite schema and existing records, operational data path, five tabs, existing synthetic stopwatch, bundled IANA timezone data, Windows batch launch and tests.
- No data migration; operational data is stored under `%LOCALAPPDATA%\\GreenLight\\FacilityIntelligence\\operational_visits.sqlite3` on Windows.
- Verification defaults to `No` for new quick-captured visits; no automatic promotion to statistical eligibility.

## Test results
- 121/121 automated tests passed under Linux virtual display, including all 112 accepted baseline tests and 9 additional capture/delay/GUI tests.
- Physical Windows testing not performed here. Founder Windows acceptance required.

## Important boundaries
- Facility directory/autocomplete is **not** implemented (D0.2). Enter observed facility codes only; never guess.
- Capture uses the Windows computer clock; saved timestamp accuracy is not independently verified. Offset changes are detectable, but an incorrect clock or forward clock adjustment without offset change cannot be reliably identified from wall-clock timestamps alone.
- Delay mapping to existing broad categories retains the specific driver choice in `delay_notes`; no schema redesign.
- `Arrived` starts a new visit only if the currently active visit is completed. Use resume for a previously saved unfinished visit.
- The historical manual-entry form retains its prior technical labels and controls; broader UI redesign remains outside this increment.

## Windows retest checklist
1. Extract into a **new** folder. Do not delete `%LOCALAPPDATA%\\GreenLight\\FacilityIntelligence`.
2. Run `Run_Tests.bat`: expect **121 tests, zero failures/errors**.
3. Launch `Launch_Green_Light.bat`, open Tab 5, enter a fictional test facility code, select Pickup and Loaded, click **Arrived**. Confirm `SAVED` status.
4. Close and restart, confirm unfinished visit is recovered. Click **Checked In**, then **Left**; confirm saved state and Completed in history.
5. Try a duplicate event; confirm it is rejected and original time remains unchanged.
6. On another fictional visit, click Arrived then Left without Checked In; confirm success.
7. Open saved visit/corrections, change a field with a correction reason, confirm history preserves original values.
8. Confirm an older operational visit, duration-only record, and existing audit history remain retrievable; test synthetic stopwatch remains independent.
9. Confirm existing records survive replacing the extracted application folder.

This is an engineering test release, **not R1.0 operational approval**.
