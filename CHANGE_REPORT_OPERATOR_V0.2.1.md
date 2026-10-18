# Operator Interface V0.2.1 — focused usability correction

## Scope
- Conditional explanation entry for the only dropdowns offering `Other`: Visit Type and Observation Source. Explanations are required for active `Other` selections, retained when hidden, and saved as `other_explanations` in the in-memory source record.
- Calendar popup dismisses on click in the main application outside the popup. Popup month navigation, selection and positioning are unchanged. No grab is used, avoiding focus capture. Escape still dismisses.
- Hour/minute and AM/PM controls receive modest padding and wider AM/PM selector.

## Verification
- 78/78 automated tests pass under a virtual graphical display, including all 71 prior tests and seven new regression tests.
- Calculation engine (`facility.py`) unchanged byte-for-byte.
- Windows click-away behavior and display scaling require founder testing on actual Windows hardware.

## Limits
- No persistent storage, cloud connection, Hive sync, live Amazon data, or dispatch features.
- Other explanations remain in memory with the fictional visit and are discarded on close.
