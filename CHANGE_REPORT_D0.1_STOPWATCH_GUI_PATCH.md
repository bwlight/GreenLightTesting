# D0.1 stopwatch GUI corrective patch

## Scope
- Mount existing `StopwatchPanel` into notebook Tab 4 with `pack(fill='both', expand=True)`.
- Keep existing HH:MM elapsed display and fictional capture workflow.
- Make `StopwatchPanel.destroy()` call idempotent `shutdown()` before Tk destroys its Tcl commands. This cancels the scheduled `after` callback even when test code destroys the parent window directly. Normal WM_DELETE_WINDOW shutdown still works.
- Add GUI tests for mounted controls, fictional arrival/check-in capture, and timer cleanup on direct panel/root destruction.

## Verification
- 112/112 Python tests pass under Linux/Xvfb (previously 110).
- No `invalid command name ... tick` warning observed in this test run.
- Windows GUI and shutdown acceptance must be independently retested.

## Unchanged
- `facility.py` calculation engine, calendar code, SQLite operational schema and location, operational audit records, bundled IANA timezone files, launcher and test runner.
- No D0.2/D0.3 or broader UI work.

## Founder Windows retest
1. Extract ZIP to a **new folder**, leaving the operational user-data folder intact.
2. Launch `Launch_Green_Light.bat`, select **4 Driver stopwatch**, confirm fictional facility field, visit type, arrival button, elapsed HH:MM, check-in, exit, correction and history controls are visible.
3. Capture fictional gate arrival and accepted check-in. Confirm elapsed HH:MM updates and saved status; exit when ready.
4. Close and reopen several times, including while a fictional stopwatch visit is active. Check console for Tcl `invalid command name ... tick` warnings.
5. Run `Run_Tests.bat`; expect **112 tests, 0 failures, 0 errors** and no callback warnings.
6. Retrieve an existing operational visit from Tab 5; confirm data and audit history remain unchanged.

This is an engineering test release, not an approved operational release.
