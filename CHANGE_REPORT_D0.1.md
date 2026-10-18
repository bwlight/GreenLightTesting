# D0.1 — Durable Visit Records

**Scope:** An isolated operational visits tab added to the accepted V0.3 engineering prototype. Frozen `facility.py` unchanged. No facility directory, Hive, cloud, or production dispatch integration.

## Storage and safety

- Tab 5 **Operational visits** is the only operational-entry workflow. Tabs 1–4 remain synthetic engineering tools; they do not feed the operational database.
- Operational records are committed to SQLite at `%LOCALAPPDATA%\GreenLight\FacilityIntelligence\operational_visits.sqlite3` on Windows. Do not delete this folder when replacing the extracted application.
- `visits` uses UUID primary keys, schema version 1, JSON fields; `revisions` preserves full before/after snapshots, UTC correction time, and mandatory reason. Initial capture is also audited.
- No migration automatically drops, replaces, or clears the operational database. No export/backup/restore UI in D0.1: these remain D0.3 requirements.
- Timestamp fields require full ISO local date/time with **explicit offset and whole seconds**, or remain blank. No timezone inferred from device or facility. An external stopwatch duration is recorded independently as seconds, with declared precision and source. It is **never converted to fabricated timestamps**.
- Completed means an exit timestamp or measured duration is supplied; incomplete is permitted. A missing facility code blocks saving. Facility directory matching and stable facility IDs are **deferred to D0.2**; entered codes are unverified text at this stage.
- Engine metrics are shown only when all three site timestamps are present; otherwise dwell is **Not available**. The duration-only measurement is shown separately, not injected into the approved engine.

## Founder test

1. Extract the ZIP to a writable folder; run `Launch_Green_Light.bat` with Python 3.10+ / Tkinter installed.
2. Open **5 Operational visits** (selected by default). Enter an observed facility code, keep **Incomplete**, and save. Confirm **SAVED** status.
3. Close the application and reopen it. Search by facility code; select the saved visit and verify all fields reload.
4. Create a **Completed** duration-only visit: enter a duration in whole seconds, choose precision and source; leave arrival/check-in/exit blank. Verify engine dwell is **Not available**, while observed duration remains intact.
5. Select a saved record, change a field, choose **Save audited correction**, and enter a reason. Inspect the full before/after audit snapshots. Cancel/blank reason must not save.
6. Try a timestamp without an offset, out-of-order site events, and a fractional-second timestamp. Confirm each is rejected without a save.
7. Replace the extracted application folder with a fresh copy; verify the same records remain. Do **not** delete `%LOCALAPPDATA%\GreenLight\FacilityIntelligence`.
8. Run `Run_Tests.bat`. Test also at the founder's Windows scaling and window size.

**Operational approval remains blocked** until D0.2 nomenclature and D0.3 export/backup/recovery plus founder Windows acceptance. This is a D0.1 testing release, not a certified operational release.
