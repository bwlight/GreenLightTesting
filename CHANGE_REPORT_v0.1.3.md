# GLFI M1 v0.1.3 — Focused duplicate-identity correction

## Executive result

**Confirmed v0.1.2 defect:** two records with the same `(source_system, source_record_id)` but different dwell times yield 60 or 120 minutes depending on input order. Both observations are preserved in v0.1.3, producing 90 minutes and `SOURCE_ID_CONFLICT_REVIEW` on each. No records were deleted.

## Changes

- Resolve source identities across the full batch, not by first encountered record.
- Suppress only repeated source records with identical observation payloads (excluding local `visit_id` and confirmation annotation); use stable `visit_id` ordering to choose a retained representative.
- Treat conflicting source-record payloads and conflicting visit IDs as human-review warnings; do not silently discard either.
- Resolve explicit confirmed-duplicate references after all IDs are indexed; unresolved, ambiguous, or reciprocal links are not automatically excluded.
- Matching timestamps and facility alone remain a suspicion, never proof of identity.

## Reproducible tests

`python -m unittest discover -s tests -v` and `python run_demo.py` (Windows: `py` instead of `python`). 38 tests passed, including 7 new order/identity tests; existing approved calculation tests remain passing. The new tests compare both input orders and stable counted identities.

## Limitations

This is a synthetic-only reference identity policy, not an authenticated import or human-confirmation workflow. Conflict warnings do not resolve underlying identity disputes. No database, interface, cloud services, production data, or live integrations. Original workbook and SPEC v1.0.0 remain unchanged. Microsoft Excel cross-engine verification is pending.
