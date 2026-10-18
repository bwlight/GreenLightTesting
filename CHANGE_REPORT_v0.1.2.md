# GLFI M1 v0.1.2 — Focused change report

**Scope:** Two independently reported v0.1.1 validation defects. No feature expansion.

1. **Appointment-only ambiguous local time:** v0.1.1 looped over site and appointment timestamps and added `AMBIGUOUS_LOCAL_TIME` to record-level issues. A synthetic `2026-11-01T01:30:00` appointment in `America/New_York` with unambiguous site timestamps thus wrongly yielded `REVIEW`. v0.1.2 checks site ambiguity separately; appointment ambiguity becomes `AMBIGUOUS_APPOINTMENT_LOCAL_TIME` warning and removes only appointment metric eligibility. Site dwell remains VALID and counted. A nonexistent spring-forward appointment receives the same conservative warning.
2. **Invalid zone with aware timestamps:** v0.1.1 `ambiguous_local` returned False immediately for aware timestamps, bypassing zone validation. v0.1.2 validates a supplied `time_zone` with `ZoneInfo` independently before evaluating ambiguity. An invalid identifier yields `INVALID_TIME_ZONE` and REVIEW even with aware timestamps. Existing invalid-zone test expectations were updated to the more accurate code.

**Regression evidence:** 26 retained tests + 5 new targeted tests = **31 passed** using Python `unittest`; synthetic demo executed. Critical approved calculation references continue to pass.

**Limitations:** No Microsoft Excel cross-engine execution; no production data or deployment; no complete DST disambiguation or workbook parity claim. Original V1 workbook was not changed. Frozen SPEC v1.0.0 remains unchanged.

**Reproduce:** Extract ZIP, open terminal in extracted folder, run `py -m unittest discover -s tests -v` (Windows) or `python3 -m unittest discover -s tests -v` (Mac/Linux), then `py run_demo.py` or `python3 run_demo.py`.
