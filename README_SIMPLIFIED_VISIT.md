# Simplified Operational Facility Visit — Windows Test

1. Extract ZIP to a writable folder and run `Launch_Green_Light.bat`.
2. Open **5 Operational visits**. The top section is for real operational SQLite records. Use **fictional test facility codes** during testing.
3. Enter the facility code, choose Pickup/Drop-off and Loaded/Empty. Click **Arrived** when reaching the facility, **Checked In** when an authorized employee confirms you are supposed to be there, and **Left** when physically departing. Check-in is not dependent on a dock assignment.
4. Each successful tap displays `SAVED`. You may close the app and resume an unfinished visit after reopening. The optional delay dropdown and notes are not required for normal visits.
5. To change a saved event, use **Open saved visit / corrections**, edit the existing manual form, and **Save audited correction** with a reason. The existing history/search panel is below.
6. Run `Run_Tests.bat` and follow `CHANGE_REPORT_SIMPLIFIED_VISIT_UI001.md` for acceptance checks.

The Windows device clock and offset are observed, not independently verified. No facility timezone is inferred. Do not operate the application while driving.
