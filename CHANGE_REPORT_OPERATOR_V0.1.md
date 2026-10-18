# Operator Interface V0.1 — Date & Time Usability

**Scope:** User-interface controls only. Frozen calculation engine `facility.py` and session adapter `operator_model.py` are unchanged from accepted Operator Interface V0.

## Changes
- `Visit date` is a read-only, clickable date field with a calendar button. The popup starts at that field's currently selected month and highlights the selected day.
- Appointment, arrival, check-in, and exit each have an independent calendar and 12-hour hour/minute/AM-PM controls.
- Appointment has a clearly labeled **No appointment** checkbox. Disabling appointment entry emits an empty appointment value; toggling it back on restores the prior selection without overwriting it.
- Dates are never automatically propagated from one timestamp field to another; overnight visits are supported.
- Input adapter converts the UI selection to the existing engine's ISO local-time string (`YYYY-MM-DDTHH:MM:00`), preserving existing semantics. The UI operates at minute precision; the engine retains its prior sub-minute support for direct/programmatic inputs.
- Existing Windows launcher retained. No third-party dependencies or cloud services.

## Regression evidence
- 45 existing tests retained and passing.
- 13 new tests: 9 pure date/time/calendar tests, 4 Tkinter GUI control tests.
- **58/58 tests passed** under Python with `xvfb-run` on Linux.
- Tkinter window construction smoke test passed under virtual display, with all five date/date-time controls instantiated.
- Independent Windows click-through remains pending founder evaluation.

## Run
- Windows: double-click `Launch_Green_Light.bat` and `Run_Tests.bat`.
- CLI: `py operator_ui.py` and `py -m unittest discover -s tests -v`.
- Linux graphical/headless testing: `xvfb-run -a python -m unittest discover -s tests -v`.

## Boundaries
Synthetic data only; in-memory session; no persistent storage, live integrations, or production authorization. The popup uses Tkinter widgets rather than the Windows native date control. The UI uses local wall-clock timestamps without entering offsets; the engine's existing time-zone validations are unchanged.
