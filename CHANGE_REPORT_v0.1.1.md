# Green Light Facility Intelligence — v0.1.1 change report

**Scope:** Offline synthetic-only hardening; frozen SPEC v1.0.0 retained unchanged.

## Defect and resolution

v0.1.0 directly compared datetime values in `assess()` and used `max(a, p)` when computing post-appointment dwell. Python raises `TypeError` for mixed naive/aware datetimes. v0.1.1 replaces those paths with guarded duration comparisons, classifies mixed site times as `REVIEW`, and treats a mixed-representation appointment as an appointment warning and metric-ineligible while retaining valid total dwell. Consistently aware timestamps compare by UTC instant.

Timestamp parsing now safely handles non-string and malformed values; malformed site times require review, and malformed appointment values remain excluded from appointment metrics. Invalid time-zone identifiers are flagged rather than crashing.

## Reproducible evidence

Run `python -m unittest discover -s tests -v` from the extracted project directory (Windows may use `py`). **26/26 tests passed** in the local execution environment: 17 original tests and nine additional regression tests (with subcases). `python run_demo.py` also executed successfully with the original synthetic output.

## Limitations

No workbook importer, user interface, persistent store, network access, production data, or live integrations. Microsoft Excel cross-engine verification is pending. Validation warnings are not evidence of actual operational safety. Site timestamps with offsets and inconsistent local visit-date conventions may require future clarification. No deployment is authorized.
