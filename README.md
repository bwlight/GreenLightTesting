# Green Light Facility Intelligence — Operator Interface V0.3

Offline, Python-standard-library-only, synthetic-data evaluation app.

## Launch on Windows
1. Extract the entire ZIP to a writable folder (for example Documents).
2. Install Python 3.10+ with Tkinter if not already installed.
3. Double-click `Launch_Green_Light.bat`.
4. Select the **4 Driver stopwatch** tab.
5. Enter a fictional facility code and click **Capture gate arrival / Start visit**. Later click **Capture accepted check-in** and **Capture physical exit**.
6. Close and reopen before completing a fictional visit to verify recovery.
7. For corrections, select an event and click **Correct timestamp (audited)**. Use a timestamp such as `2026-10-15T23:59:05-05:00` and give a reason.

The HH:MM stopwatch is a display; each recorded event retains seconds. The database is created automatically at `local_data/synthetic_stopwatch.sqlite3` in the extracted folder. **Do not delete that folder if you want to keep the fictional stopwatch records.** The separate manual-entry tab remains unsaved.

## Tests
Double-click `Run_Tests.bat` or run `python -m unittest discover -s tests -v` in the extracted folder. 98 tests passed on the development environment with a virtual display.

See `CHANGE_REPORT_OPERATOR_V0.3.md` for policy and limitations. No cloud or live integrations.
