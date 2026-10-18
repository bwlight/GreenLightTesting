# Frozen requirements — SPEC v1.0.0

**Freeze authorized:** Founder authorization, 2026-10-11. **Scope:** isolated offline calculation-validation prototype, synthetic data only. All F-01–F-04 policies approved. Seven corrected reference cases T12, T13, T17, T19, T20, T21, T23 approved subject to decimal half-up rounding tests. Original V1 baseline remains unchanged. Microsoft Excel independent cross-engine verification is pending and accepted as an offline-prototype-only risk. Implementation correctness must be proven separately from requirements freeze.

The following is the frozen technical requirements text inherited from accepted SPEC v0.2.1. Earlier historical references to pending freeze authorization describe the pre-freeze state and are superseded by this cover statement. No SaaS, cloud, production data, Amazon, or ELD integration is authorized.

---

# Green Light Logistics — Facility Intelligence
## M1 Requirements & Synthetic Test Specification

**Document ID:** GLL-FI-M1-SPEC  
**Version:** 0.2.1 (consolidated working draft; requirements not frozen)  
**Date:** 2026-10-12  
**Baseline:** `Green_Light_Amazon_Facility_Intelligence_V1.xlsx`  
**Approval status:** Accepted as current working draft after independent review; not yet frozen as an implementation baseline  
**Scope:** Data integrity and calculation parity only. No application code, live integrations, HOS calculations, or SaaS deployment.

### Executive summary — founder review first

**Decision status:** The founder approved three measurement policies and accepted T12/T13 legacy-defect reproduction in the tested evaluator. All four previously pending policy decisions F-01–F-04 have been resolved. The table below is an approval record, **not a list of outstanding approvals**:

| ID | Approval question | Engineering recommendation | Current status |
|---|---|---|---|
| F-01 | What is the operational meaning of the unusual appointment-after-exit flag? | Retain general VALID and T=0; add a separate non-exclusionary `APPOINTMENT_AFTER_EXIT` review warning, visible in quality reports | **APPROVED: separate non-exclusionary warning** |
| F-02 | Which timestamp anomalies must block metric eligibility? | Require numeric appointment and unambiguous local chronology for appointment-specific averages; preserve original observation and do not auto-rewrite | **APPROVED: preserve raw values; separate appointment eligibility** |
| F-03 | How should duplicate observations be treated in M1? | Preserve originals; identify exact synthetic duplicate attempts as warnings; postpone automatic deduplication | **APPROVED: conservative suspected-vs-confirmed identity policy** |
| F-04 | Are non-Excel execution results sufficient to freeze the implementation baseline? | Obtain an independent Microsoft Excel recalculation or record an explicit waiver and risk acceptance | **APPROVED: Excel verification remains pending; waiver requires explicit recorded risk acceptance** |

**Engineering recommendation:** Review the independent corrected reference results in §12, then decide whether to freeze requirements as v1.0.0 and separately authorize a small isolated prototype. Do not modify baseline V1, purchase services, or deploy cloud infrastructure.

**Confirmed:** T12 legacy Master row 41 = 0 vs positional-control row 5 = 2; T13 legacy appointment average = 30 minutes despite one eligible 60-minute observation. These were executed with `artifact_tool`, not Microsoft Excel. **Corrected outputs are now independently calculated reference oracles (§12), not results from a corrected workbook or application.**

**Source integrity:** Baseline SHA-256 `fccf2edf44d09066a6cdbc3de56d2fd2e13bccb6a62d9f0e33f9e310dd8e0a14` (recorded for this revision). Evidence: `GLFI_M1_T12_T13_Execution_Evidence_v0.1.0.md` and three disposable fixture workbooks.

### 0. Version history

| Version | Change | Evidence |
|---|---|---|
| 0.1.0 | Initial static analysis, proposed requirements and T01–T18 | Original baseline inspection |
| 0.2.0 | Founder-approved semantics, executed T12/T13 evidence, refined tests, explicit legacy/corrected oracles and acceptance gates | Founder decisions + execution evidence v0.1.0 |
| 0.2.1 | Approved F-01–F-04 policy record; conservative duplicate identity; additional artifact_tool legacy test evidence; independently calculated corrected reference oracles | Remaining synthetic evidence v0.2.0-E1 and §12 |

### 1. Evidence legend and change control

- **[V] Verified static workbook:** observed in worksheet labels, formula text, or validation definitions. Not an executed Excel test.
- **[T] To test:** an expected result requiring execution against a disposable workbook copy.
- **[P] Proposed correction:** behavior not established by V1 and requiring approval.
- **[A] Assumption/open decision:** not yet resolved.

Do not overwrite the baseline workbook. Record source-file checksum, spreadsheet application/version, locale, date system, test fixture version, formula cell references, observed results, and discrepancies for every executed test. A test result is not 'verified' merely because a formula was inspected. Do not use live customer data in test fixtures.

### 2. Source inventory and existing behavior

[V] Five worksheets: `Start Here`, `Visit Log`, `Facility Master`, `Dashboard`, `Definitions`.

[V] `Visit Log` columns A:N are source inputs: Visit Date; Trip Ref; Facility Code; Facility City / State; Visit Type; Trailer Context; Appointment Date/Time; Arrival Date/Time; Check-in Date/Time; Released / Exit Date/Time; Verified; Delay Cause; Delay Notes; Source. Columns O:V are derived: Arrival vs Appt (min); Arrival to Check-in (min); Check-in to Exit (min); Total Site Dwell (min); Early Arrival (min); Post-Appt Dwell (min); Data Quality; Facility Delay Flag. Preconfigured data rows 5:154.

[V] Visit Log dropdowns: E {Pickup, Drop-off, Other}; F {Loaded, Empty, Bobtail, Unknown}; K {Yes, No}; L {Facility, Driver, Equipment, Traffic, Weather, Mixed, Unknown, None}; N {Firsthand, Driver report, Other}. Master C has Visit Type dropdown. Dropdown presence is not proof of robust import validation.

[V] Quality gate `Visit Log!U5`: blank if `COUNTA(A5:N5)=0`; otherwise REVIEW if K != Yes, A not numeric, C blank, E blank, H/I/J not numeric, I < H, J < I, or INT(H) != A; otherwise VALID. No requirement that G (appointment) be populated. This is a formula rule, not independent proof of timestamp accuracy.

[V] O = ROUND((H-G)*1440,1) if both present; P = ROUND((I-H)*1440,1) when ordered; Q = ROUND((J-I)*1440,1) when ordered; R = ROUND((J-H)*1440,1) when ordered; S = MAX(0, ROUND((G-H)*1440,1)); T = MAX(0, ROUND((J-MAX(G,H))*1440,1)) when G,H,J present and J>=H. Note: T may yield zero when appointment is after departure. V maps VALID+Facility to Facility-coded, VALID+Mixed to Mixed cause, other VALID to Not attributed; invalid to blank.

[V] `Facility Master` A:N: Facility Code; City / State; Visit Type; Valid Visits; Mean Dwell; Mean Check-in→Exit; Mean Early Arrival; Mean Post-Appt Dwell; Max Dwell; Facility-coded Delays; Last Visit; Confidence / Sample; Local Notes; Review. Manual index rows 5:44, keyed in practice by code + visit type but not uniqueness-enforced. Metrics use SUMIFS/COUNTIFS/MAXIFS and a denominator of D (all valid visits). Sample bands: 0 NO DATA; 1–4 EARLY SAMPLE; 5–19 DEVELOPING; 20+ LARGER SAMPLE. Labels are not statistical confidence intervals.

[V] `Dashboard!B5:B12`: valid visit count, review count, total dwell hours, average total dwell, average post-appointment dwell, facility-coded delay count, pickup count, drop-off count. B9 divides the SUMIF of T for VALID rows by B5 (all valid rows).

[V] Workbook definitions: physical arrival means joining entrance/gate queue; check-in means accepted check-in/processing start; exit means physical clearance; all times are facility-local with full dates for overnight visits; do not attribute all dwell to facilities; driver dwell is distinct from carrier administrative workload; pseudonymous trip refs are preferred.

### 3. Defects and controlled behavioral changes

**DEF-001 — Moving Master source ranges [V/T].** `Facility Master!D5` uses `Visit Log!$C$5:$C$154`; `D6` uses `$C$6:$C$154`; `D41` uses `$C$41:$C$154`. The same advancing-start pattern appears in summary metrics. Thus a Master row below an earlier matching Visit Log record can undercount. [P] Fixed range 5:154 for all Master rows, or in future database query all eligible visits independent of physical row placement. Preserve original V1 observed result as the *legacy oracle*, and the corrected result as the *approved oracle*.

**DEF-002 — Appointment denominator [V/T; executed].** `Facility Master!H5` and `Dashboard!B9` sum T but divide by all VALID visits. VALID does not require appointment G; blank T contributes no value to the numerator while the visit contributes to denominator. [APPROVED] Use only VALID visits with a *calculable* post-appointment measure as denominator; no appointment means total-dwell eligible but appointment-metric ineligible. [APPROVED WITH FLAG] Appointment after physical exit retains T=0; attach an explicit anomaly review warning without silently changing or discarding the observation. The approved representation is a separate non-exclusionary warning; it does not change general VALID status.

**DEF-003 — No distinct measure eligibility flags [APPROVED].** Preserve general VALID for total dwell and separate eligibility for appointment-based measures. Missing G alone must not convert an otherwise valid visit into REVIEW. Appointment-after-exit generates a separate warning; do not conflate warning with legacy general REVIEW status.

**DEF-004 — Finite and manual indexes [V/P].** Visit Log 5:154; Master 5:44. Future queries must not depend on worksheet row position or manual Master registration. This is out of scope for Excel correction except targeted regression tests.

### 4. Normative requirements (proposed acceptance baseline)

| ID | Requirement | Origin | Verification |
|---|---|---|---|
| R-001 | Preserve every original A:N input and provenance; never replace original timestamps with derived durations. | V/P | Field-mapping audit |
| R-002 | Preserve one record per actual visit, including separate pickup/drop-off visits when distinct. | V | Scenario T11 |
| R-003 | Reproduce V1 general quality classification on approved legacy-parity tests. | V | T01–T10 |
| R-004 | Calculate signed appointment variance, queue time, post-check-in time, total dwell, early arrival, and post-appointment dwell with documented one-decimal rounding. | V | T01–T07 |
| R-005 | Exclude REVIEW rows from qualifying summary metrics. | V | T04/T05/T08 |
| R-006 | Group summaries by facility code and visit type; include qualifying visits irrespective of physical source row. | P (DEF-001) | T12 |
| R-007 | Compute appointment means using only VALID visits with a calculable appointment measure; disclose eligible count, including zero-valued eligible measurements. | Founder approved (DEF-002) | T07/T13/T17/T19 |
| R-008 | Maintain human-coded delay cause separately from observed dwell. | V | T09/T10 |
| R-009 | Distinguish no data from numeric zero; do not invent a mean with no eligible observations. | V/P | T13 |
| R-010 | Use pseudonymous trip references; synthetic fixtures must contain no personal or shipment-confidential information. | V | Fixture audit |
| R-011 | Retain source version, rule version, and explicit legacy-vs-corrected comparison for any changed metric. | P | Report audit |
| R-012 | Avoid dependence on Amazon APIs, ELDs, cloud hosting, or production credentials in M1. | P | Scope review |
| R-013 | Document time zone and daylight-saving ambiguity without pretending Excel local timestamps resolve it. | P | T16 |
| R-014 | Preserve or explicitly document Excel's rounding and missing-value semantics, including a possible zero post-appointment dwell. | V/approved | T02/T17/T20 |
| R-015 | When appointment occurs after physical exit, preserve source times and T=0 while emitting a separate non-silent review flag. | Founder approved with flag | T17/T21 |
| R-016 | Store separate legacy V1 and corrected expected results for every intentional formula change; do not alter original V1 workbook. | Founder approved | T12/T13, evidence audit |
| R-017 | Verify that valid zero appointment measurements contribute to eligible denominator, while missing measurements do not. | Derived from approved policy | T19 |
| R-018 | Preserve distinct local wall time, offset/time-zone provenance (when known), and unresolved ambiguity; do not fabricate elapsed durations at DST transitions. | Proposed | T16/T22 |
| R-019 | Preserve source-row independence in all corrected facility summaries, including counts, mean, maximum, delays and last visit. | Proposed correction | T12/T23 |

### 5. Synthetic test data specification

All timestamps are fictional facility-local times on 2026-10-15 unless otherwise stated. For each scenario, set Visit Date equal to the arrival calendar date; use `Verified=Yes`, `Visit Type=Pickup`, `Trailer Context=Loaded`, `Delay Cause=None`, `Source=Firsthand` unless overridden. Record exact cell placements and formula outputs. Each scenario must be independently reset unless explicitly marked a multi-row fixture. Expected minutes are based on the documented definitions, not cached workbook values.

| ID | Fixture / event times | Legacy V1 expectation | Corrected expectation | Priority |
|---|---|---|---|---|
| T01 | F-A; appt 10:00, arrival 10:00, check-in 10:15, exit 11:00 | VALID; R=60, P=15, Q=45, T=60 | Same | P1 |
| T02 | F-A; appt 10:00, arrival 09:30, check-in 09:50, exit 11:15 | VALID; O=-30, P=20, Q=85, R=105, S=30, T=75 | Same | P1 |
| T03 | F-A; appt 10:00, arrival 10:20, check-in 10:30, exit 11:00 | VALID; O=+20, R=40, T=40 | Same | P2 |
| T04 | F-A; arrival 10:00, check-in 09:59, exit 11:00 | REVIEW; P blank | Same | P1 |
| T05 | F-A; arrival 10:00, check-in 10:10, exit 10:09 | REVIEW; Q blank | Same | P1 |
| T06 | F-A; arrival 2026-10-15 23:30, check-in 23:50, exit 2026-10-16 01:00 | VALID; R=90 | Same | P1 |
| T07 | F-A; appointment blank, arrival 10:00, check-in 10:10, exit 11:00 | VALID; R=60; T blank | VALID for dwell; appointment-ineligible | P1 |
| T08 | F-A; otherwise T01 but Verified=No | REVIEW; excluded | Same | P1 |
| T09 | F-A; otherwise T01 but Delay Cause=Facility | V=Facility-coded | Same; attribution not independent proof | P2 |
| T10 | F-A; otherwise T01 but Delay Cause=Mixed | V=Mixed cause | Same | P2 |
| T11 | Two separate F-A visits: Pickup R=60, Drop-off R=120 | Distinct summaries if both Master rows registered | Same, without manual registration dependency | P1 |
| T12 | Place F-A Pickup valid visits in Visit Log rows 5 and 6 (R=60 and R=120); register F-A Pickup in Facility Master row 41 | Master D41=0 (rows 5,6 excluded), E41 blank; Dashboard B5=2 | Master count=2, mean dwell=90 | **P0** |
| T13 | Two F-A Pickup VALID visits: T01 (T=60) and T07 (T blank); register F-A Pickup at Master row 5 | Master D5=2; H5=30; Dashboard B9=30 | Appointment-eligible count=1; mean T=60 | **P0** |
| T14 | Same synthetic visit imported twice | V1 has no proven duplicate-prevention mechanism | Import should flag or prevent duplication by documented identity policy | P2 |
| T15 | Arrival 2026-10-15 10:00, exit 2026-10-18 10:00, ordered check-in | V1 can classify VALID if other required fields satisfy U | Proposed anomaly warning; threshold TBD | P3 |
| T16 | Facility-local visit crosses DST fall-back hour; no offset supplied | Excel cannot disambiguate repeated local time | Explicit ambiguous-time warning; no invented elapsed duration | P3 |
| T17 | Appt 12:00, arrival 10:00, check-in 10:10, exit 11:00 | VALID; T=0 by MAX(0, ...) | VALID for total dwell; T=0 preserved; `APPOINTMENT_AFTER_EXIT` warning; no silent exclusion | **P0** |
| T18 | Blank A:N row with formula columns prefilled | U blank; not counted | Same | P2 |
| T19 | Three VALID F-A pickups: T=60, T=0 (appointment exactly at exit), and T blank (missing appointment) | Legacy denominator 3; appointment mean 20 | Eligible denominator 2; mean 30; zero included, blank excluded | **P0** |
| T20 | Arrival 10:00:00, check-in 10:00:03, exit 10:00:09; all timestamps numeric | Excel minute calculations rounded to one decimal; capture actual engine behavior | Explicit one-decimal parity; record raw precision and no premature rounding | P1 |
| T21 | Two VALID F-A visits: one normal T=60 and one appointment after exit T=0 | Legacy general VALID for both, appointment mean 30 | Mean 30 if both calculable; anomaly warning on second; no automatic removal | **P0** |
| T22 | Missing/invalid date serial, text timestamp, or Visit Date ≠ INT(arrival) | REVIEW per U formula | Preserve legacy REVIEW for general eligibility; error reason captured separately | P1 |
| T23 | F-A visits in rows 5,6 with Master F-A entry row 41; include facility delay and last visit fields | Legacy row-41 aggregates may omit early visits | All corrected summary metrics independent of Master row; verify count, mean, max, delay count, last visit | P1 |
| T24 | Duplicate facility code/type appears twice in Master | V1 does not enforce unique Master index | Future summaries have unique facility/type grouping; preserve any legacy note conflicts for manual review | P2 |

**T12 reproduction instructions:** Work only in a disposable workbook copy. Clear test inputs, place two valid F-A Pickup records at Visit Log rows 5 and 6, enter `F-A` and `Pickup` in Master row 41, recalculate in a supported spreadsheet engine, record `D41`, `E41`, `Dashboard!B5`, and formula text. Repeat with identical Master entry in row 5 to demonstrate row-position sensitivity. Do not modify formulas during the legacy run.

**T13 reproduction instructions:** Work in a separate disposable copy. Place two valid F-A Pickup visits in Visit Log rows 5 and 6, with total dwell 60 minutes each. Give row 5 an appointment equal to arrival, producing T=60; leave row 6 appointment blank, producing T blank. Enter F-A/Pickup at Master row 5. Capture `U5`, `U6`, `T5`, `T6`, `D5`, `H5`, `Dashboard!B5`, `Dashboard!B9`. Expected legacy H5 and B9 are 30; corrected mean is 60 with one eligible visit. These legacy outcomes were executed and confirmed in artifact_tool under evidence v0.1.0. Independent Microsoft Excel recalculation remains pending; corrected intended results have not been executed.

### 6. Test execution and evidence format

For each case record: test ID; fixture revision; workbook hash; spreadsheet engine/version; date/locale settings; cell coordinates; expected V1 output; actual V1 output; approved corrected output; pass/fail/blocked; discrepancy ID; reviewer; date. Attach a copy of formula text and a concise input/output table for P0 cases. If Excel/LibreOffice behavior differs, preserve both outputs rather than silently selecting one. Explicitly test empty cells vs empty strings, date serials, one-decimal rounding, and cached-versus-recalculated values.

**Gate G1 — Baseline reproduction: PASS in artifact_tool.** T12 and T13 matched legacy predictions; positional control confirmed row dependence. Independent Microsoft Excel verification remains pending.  
**Gate G2 — Semantics approval: PASS for F-01–F-04 founder policies.** Independent Excel execution and time-zone reference validation remain pending evidence, not unapproved policies.  
**Gate G3a — Corrected reference oracle: READY FOR INDEPENDENT REVIEW.** Critical P0 corrected results have been calculated without modifying V1 (§12). Reviewer sign-off is pending. **Gate G3b — Implementation parity: NOT TESTED.** No corrected application exists; its behavior cannot yet be claimed correct. Additional legacy test coverage is documented in the evidence report.  
**Gate G4 — Professional handoff: PENDING.** An independent reviewer must be able to reproduce from baseline workbook, fixture catalog, precise cell placement, environment/version, source hash, expected/observed outputs and discrepancy log without credentials.

### 7. Logical data model (design only, not implementation)

- **Facility:** internal facility ID, external code, location, optional IANA time zone; code uniqueness scope to be decided.
- **FacilityVisit:** immutable visit ID, facility ID, visit type, trailer context, pseudonymous trip ref, appointment/arrival/check-in/exit timestamps, original source values, verification attestation, delay cause/notes, provenance.
- **QualityAssessment:** visit ID, general quality status, metric-specific eligibility, issue codes, rule version, assessment timestamp.
- **FacilityNote:** facility ID, optional visit type, note, provenance, timestamp; preserves Master local notes.
- **Derived summary/view:** counts and metrics grouped by facility and visit type, with both numerator and eligible denominator disclosed. Do not store independently editable duplicate averages.

The Excel `Facility Master` is a manually maintained *reporting index*, not evidence that a separate mutable facility-summary record is needed in a database. The Visit Log is the authoritative observation source.

### 8. Deferred commercialization constraints

Future SaaS may require organization/tenant identity, carrier identity separate from tenant identity, user access control, row-level isolation, audit history, data retention, consent and cross-tenant aggregation policy, provider-specific licensing, and integration adapters. **No multi-tenant implementation is required in M1.** To avoid future lock-in, use stable internal IDs, source provenance, explicit metric versions, and no dependency on worksheet row numbers. Do not assume a facility code is globally unique across networks or that contributing customer data can be pooled commercially.

### 9. Founder decisions, remaining approvals, and test priority

**Decisions recorded as approved:**
- **DEC-001:** No appointment => may remain generally VALID and count for total dwell; excluded from appointment-based averages.
- **DEC-002:** Appointment later than physical departure => retain zero post-appointment dwell, preserve original timestamps, issue separate review warning.
- **DEC-003:** Report legacy V1 and corrected intended values separately; do not overwrite the original V1 workbook.
- **DEC-004:** T12/T13 execution evidence accepted as valid for the tested spreadsheet environment, not a claim of Microsoft Excel verification.

**Remaining approvals:** No outstanding F-01–F-04 policy decisions. The next explicit approval is the requirements freeze and, separately, permission to start a small isolated prototype. Microsoft Excel cross-engine verification may remain a documented risk if the founder accepts it; no automatic waiver is implied. Facility-code uniqueness scope, duration warning thresholds, and tenant boundaries are deferred nonblocking design choices.

**Execution order:**
1. **P0:** T12/T13 (already reproduced), T17, T19, T21; use disposable workbook copies and capture legacy results; separately calculate corrected reference results without changing baseline.
2. **P1 timestamp/quality:** T04–T08, T20, T22; include midnight crossing, missing G, date mismatch, seconds/rounding, and invalid ordering.
3. **P1 aggregation:** T01–T03, T11, T23; verify Master/Dashboard parity and row-independent corrected oracles.
4. **P2/P3:** T09, T10, T14–T16, T18, T24; include DST ambiguity and duplicate handling, clearly labeling unapproved policy choices.

**Test evidence requirements:** For each test, record immutable baseline hash, fixture revision, actual synthetic A:N values and source row numbers, Master index row, formula text, engine/version, locale/date system, cached vs recalculated status, legacy expected/actual, corrected expected/actual or NOT EXECUTED, warning codes, pass/fail and reviewer. Maintain a separate discrepancy register (`ID`, severity, source, reproducibility, resolution, approval).

**Corrected-oracle rule:** The corrected result is a *specified expectation*, not a test result, until an independent reference calculation is performed. Any disposable corrected-formula experiment must be explicitly labeled, retained separately, and must never replace the original baseline.

### 10. Milestone exit deliverables

1. Approved requirements specification v1.0.0.
2. Synthetic fixture catalog with expected values and source-row placement.
3. Baseline spreadsheet-evaluator execution evidence for T12 and T13; independent Excel recalculation or documented waiver.
4. Approved correction decisions and discrepancy log.
5. Portable calculation parity report; no production integration or application code.

**Status:** v0.2.1 accepted working draft; calculation-reference review pending. T12/T13 legacy outputs are confirmed in artifact_tool. Additional legacy evaluator results are recorded in `GLFI_M1_Remaining_Synthetic_Evidence_v0.2.0.md`. Corrected functionality remains unimplemented. Critical corrected expected values have independently calculated reference checks in §12; they are not corrected-software execution evidence. No application implementation authorized.

### 11. Amendment 0.2.1 — conservative duplicate identity and executed test update

**Founder-approved identity rule:** Identical facility codes and timestamps, even with similar trip references, are only a *suspected match*. Preserve both observations for human review. Only a trusted repeated source-record identity or an auditable human-confirmed duplicate may be excluded from counting. Keep an audit trail of excluded repeated imports. Genuinely separate physical visits may share timestamps and must remain independently countable. V1 has no importer, so T14's legacy double-entry exercise does **not** establish import idempotency.

**Execution evidence:** `GLFI_M1_Remaining_Synthetic_Evidence_v0.2.0.md` records observed artifact_tool legacy results for T01–T11, T14–T15, T17–T24 except T16, with limitations for tests whose intended behavior needs new functionality. T12/T13 remain separately confirmed in accepted evidence v0.1.0. These results do not constitute Microsoft Excel verification or corrected-implementation parity.

**Next gate:** Review §12 corrected-reference calculations; perform selected Microsoft Excel recalculations if available; decide on v1.0.0 requirements freeze and separate isolated-prototype authorization. DST disambiguation, importer identity and warning generation remain future implementation tests, not prerequisites to define core calculation requirements.


### 12. Independently calculated corrected reference results (0.2.1 consolidation)

**Method:** Arithmetic from the synthetic inputs and previously recorded legacy evidence, independently of Excel formulas and `artifact_tool`. Results below are **reference expectations**, not execution of corrected software. Duration calculations use exact elapsed seconds converted to minutes and rounded to one decimal at the individual-visit measure, following V1's intended convention. Aggregate means are computed from those eligible per-visit measures; display precision must be specified at implementation. An absent appointment is *missing*, not numeric zero.

| Case | Synthetic inputs / relevant observations | Independently derived corrected result | Legacy artifact_tool evidence | Status |
|---|---|---|---|---|
| T12 | F-A Pickup, visits on Visit Log rows 5 and 6, dwell 60 and 120; Master key on row 41 | Valid count **2**; mean dwell **(60+120)/2=90 min**; row placement immaterial | Master row 41 count **0**, positional-control row 5 count **2** | Corrected reference calculated; implementation untested |
| T13 | Two VALID visits; T values 60 and missing (no appointment) | Appointment-eligible count **1**; mean **60/1=60 min**; total-dwell count **2** | Master/Dashboard appointment mean **30 min** | Corrected reference calculated; implementation untested |
| T17 | Arrival 10:00, exit 11:00, appointment 12:00; verified and ordered site timestamps | Total dwell **60 min**; post-appointment dwell **max(0, 11:00−12:00)=0 min**; eligible appointment count **1**; separate `APPOINTMENT_AFTER_EXIT` warning; general status VALID | T=0; U=VALID; no warning in V1 | Corrected reference calculated; warning untested |
| T19 | Three VALID visits with T values 60, 0 and missing | Eligible count **2**; sum **60 min**; mean **60/2=30 min**; valid total-dwell count **3** | Appointment mean **20 min** | Corrected reference calculated; implementation untested |
| T21 | Two VALID visits with T values 60 and 0 (second appointment after exit) | Eligible count **2**; mean **(60+0)/2=30 min**; one non-exclusionary warning | Mean **30 min**; no warning | Corrected reference calculated; warning untested |
| T23 | F-A Pickup visits with dwell 60 and 120 on early Visit Log rows, Master key row 41; one facility-coded delay; later visit dated 2026-10-15 | Count **2**; mean dwell **90 min**; max **120 min**; facility-coded count **1**; last visit **2026-10-15** | Master row 41 count **0**, Dashboard mean **90 min** | Corrected reference calculated; implementation untested |
| T20 | Arrival 10:00:00; exit 10:00:09 | Exact **9/60=0.15 min**; one-decimal half-up rounding **0.2 min** | **0.2 min** | Rounding reference calculated; test alternate tie cases in Excel |

**Reference invariants:** For each valid visit with ordered timestamps, `total_dwell = (exit−arrival)` in elapsed minutes; the *unrounded* components arrival→check-in and check-in→exit sum to total dwell. Because each workbook metric rounds individually to one decimal, displayed rounded components may differ from rounded total by 0.1 minute. Appointment mean denominator equals the count of VALID visits with a numeric, calculable appointment-specific value, **including zero**, and excludes missing/noncalculable values. Row order and Facility Master placement cannot affect corrected aggregates. An anomaly warning does not itself change general VALID or the appointment denominator.

**Boundary and identity notes:** T17/T21 appointment-after-exit values are included because the founder explicitly approved zero plus warning. DST ambiguous local timestamps (T16) require additional zone/offset evidence; do not invent elapsed time. T14 identical facility/timestamps alone indicate *suspected* duplicates only. Preserve both records; only trusted repeated source-record identity or auditable human confirmation may prevent confirmed duplicate counting. Import idempotency remains untested until an importer exists.

#### Practical Microsoft Excel cross-engine verification plan

1. Use **read-only baseline V1** plus fresh disposable fixture copies; verify baseline SHA-256 against the recorded value. Do not open the source for editing or save over it.
2. Open T12 and T13 disposable fixtures in desktop Microsoft Excel (record product version/build, operating system, date system, locale, and calculation mode). Set calculation to Automatic; force full recalculation with `Ctrl+Alt+Shift+F9` on Windows where supported; save **new** recalculated fixture copies.
3. For T12 record `Visit Log!U5:U6`, `Facility Master!D41:E41`, `Dashboard!B5`; repeat positional-control fixture and record `Facility Master!D5:E5`. For T13 record `Visit Log!U5:U6`, `T5:T6`, `Facility Master!D5`, `H5`, `Dashboard!B5`, `B9`. Record formulas as well as displayed values; distinguish actual recalculation from pre-existing cached values.
4. If available, use additional disposable fixtures for T17, T19, T21 and T20 to verify zero-versus-missing and rounding behavior. No new corrected formulas are necessary for **legacy** cross-engine verification.
5. Compare Excel outcomes with accepted `artifact_tool` results. Record any mismatch with exact inputs, engine version, cell, observed value and severity; do not silently rewrite the oracle. If desktop Excel is unavailable, document **cross-engine verification pending** and let the founder explicitly accept that limited risk at the freeze gate.

#### Requirements freeze versus prototype correctness

**Recommended freeze gate:** A reviewer signs off on the seven corrected reference rows above, approved warning and duplicate semantics, field preservation, and known out-of-scope cases. The requirements may then be versioned **v1.0.0**. Independent Excel execution is strongly preferred but is not inherently a prerequisite if its absence is recorded and explicitly accepted.

**Separate prototype gate:** Founder authorization is required to start a small, isolated, offline implementation. Its own tests must prove parity against the frozen oracles and report differences from legacy V1. Freezing requirements does **not** establish that any implementation is correct. No production deployment, live integrations, cloud expense, or SaaS commitments are authorized by this document.
