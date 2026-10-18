"""Offline synthetic-only Facility Intelligence M1 calculation reference.

No network, database, workbook mutation, or production-data connectors.
"""
from collections import defaultdict
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

RULE_VERSION = 'M1-1.0.0'  # Frozen requirements; prototype release v0.1.3
VALID_TYPES = {'Pickup', 'Drop-off', 'Other'}
CAUSES = {'Facility', 'Driver', 'Equipment', 'Traffic', 'Weather', 'Mixed', 'Unknown', 'None'}


def minute_round(seconds):
    """Excel-like one-decimal half-away-from-zero for minute durations."""
    return (Decimal(str(seconds)) / Decimal('60')).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)


def parse_time(value):
    """Strict ISO timestamp parser; malformed input is represented as missing."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError, OverflowError):
        return None


def ambiguous_local(dt, zone_name):
    """Flag ambiguous or nonexistent naive local times; invalid zones are unsafe."""
    if dt is None or not zone_name or dt.tzinfo is not None:
        return False
    try:
        zone = ZoneInfo(zone_name)
        from datetime import timezone
        a = dt.replace(tzinfo=zone, fold=0)
        b = dt.replace(tzinfo=zone, fold=1)
        # Different offsets imply either a fold or a spring-forward gap.
        if a.utcoffset() != b.utcoffset():
            return True
        return a.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None) != dt
    except (ZoneInfoNotFoundError, TypeError, ValueError, OverflowError):
        return True


def minutes_between(start, end):
    if start is None or end is None:
        return None
    if (start.tzinfo is None) != (end.tzinfo is None):
        return None
    try:
        if start.tzinfo is not None:
            from datetime import timezone
            seconds = (end.astimezone(timezone.utc) - start.astimezone(timezone.utc)).total_seconds()
        else:
            seconds = (end - start).total_seconds()
        return minute_round(seconds)
    except (ValueError, OverflowError, TypeError):
        return None


def assess(raw):
    """Classify observations without throwing on malformed/mixed timestamp inputs."""
    r = dict(raw)
    a, c, x, p = (parse_time(r.get(k)) for k in ('arrival', 'check_in', 'exit', 'appointment'))
    issues, warnings = [], []
    if r.get('verified') != 'Yes': issues.append('NOT_VERIFIED')
    if not r.get('facility_code'): issues.append('MISSING_FACILITY')
    if r.get('visit_type') not in VALID_TYPES: issues.append('INVALID_VISIT_TYPE')
    if not a or not c or not x: issues.append('MISSING_OR_INVALID_SITE_TIME')
    if a and r.get('visit_date') != a.date().isoformat(): issues.append('VISIT_DATE_MISMATCH')
    if r.get('delay_cause', 'None') not in CAUSES: warnings.append('UNKNOWN_DELAY_CAUSE')

    site_times = (a, c, x)
    all_times = (a, c, x, p)
    site_mixed = any(t is not None and t.tzinfo is None for t in site_times) and any(t is not None and t.tzinfo is not None for t in site_times)
    appointment_mixed = p is not None and a is not None and ((p.tzinfo is None) != (a.tzinfo is None))
    if site_mixed: issues.append('MIXED_TIMEZONE_REPRESENTATION')
    if appointment_mixed: warnings.append('MIXED_APPOINTMENT_TIMEZONE')
    zone = r.get('time_zone')
    if zone is not None and zone != '':
        # Validate the identifier independently of timestamp awareness.
        # Aware timestamps previously bypassed invalid-zone detection.
        try:
            if not isinstance(zone, str):
                raise TypeError('Time zone identifier must be a string')
            ZoneInfo(zone)
        except (ZoneInfoNotFoundError, TypeError, ValueError, OverflowError):
            issues.append('INVALID_TIME_ZONE')
        else:
            # Site measurements and appointment measurements have separate
            # eligibility: an ambiguous appointment must not poison site dwell.
            if any(ambiguous_local(dt, zone) for dt in site_times):
                issues.append('AMBIGUOUS_LOCAL_TIME')
            if ambiguous_local(p, zone):
                warnings.append('AMBIGUOUS_APPOINTMENT_LOCAL_TIME')

    # Use safe duration comparison instead of Python datetime relational operators.
    queue_delta = minutes_between(a, c)
    check_exit_delta = minutes_between(c, x)
    dwell_delta = minutes_between(a, x)
    if queue_delta is not None and queue_delta < 0: issues.append('CHECK_IN_BEFORE_ARRIVAL')
    if check_exit_delta is not None and check_exit_delta < 0: issues.append('EXIT_BEFORE_CHECK_IN')
    if dwell_delta is not None and dwell_delta < 0: issues.append('EXIT_BEFORE_ARRIVAL')
    if all(t is not None for t in site_times) and any(v is None for v in (queue_delta, check_exit_delta, dwell_delta)):
        if 'MIXED_TIMEZONE_REPRESENTATION' not in issues:
            issues.append('UNCOMPARABLE_SITE_TIMES')

    appointment_provided = r.get('appointment') not in (None, '')
    if appointment_provided and p is None: warnings.append('INVALID_APPOINTMENT')
    arrival_appt = minutes_between(p, a)
    appointment_exit = minutes_between(p, x)
    if p is not None and appointment_exit is not None and appointment_exit < 0:
        warnings.append('APPOINTMENT_AFTER_EXIT')
    if p is not None and (arrival_appt is None or appointment_exit is None):
        if 'MIXED_APPOINTMENT_TIMEZONE' not in warnings:
            warnings.append('UNCOMPARABLE_APPOINTMENT')
    valid = not issues
    queue = queue_delta if queue_delta is not None and queue_delta >= 0 else None
    check_exit = check_exit_delta if check_exit_delta is not None and check_exit_delta >= 0 else None
    dwell = dwell_delta if dwell_delta is not None and dwell_delta >= 0 else None
    early = max(Decimal('0.0'), -arrival_appt) if arrival_appt is not None else None
    eligible = (valid and p is not None and arrival_appt is not None
                and appointment_exit is not None
                and 'AMBIGUOUS_APPOINTMENT_LOCAL_TIME' not in warnings)
    if eligible:
        # max(0, exit - max(arrival, appointment)), using instant-safe deltas.
        post = max(Decimal('0.0'), min(dwell_delta, appointment_exit))
    else:
        post = None
    return {'source': r, 'rule_version': RULE_VERSION, 'quality': 'VALID' if valid else 'REVIEW',
            'issues': issues, 'warnings': warnings, 'appointment_eligible': eligible,
            'arrival_vs_appointment': arrival_appt, 'arrival_to_check_in': queue,
            'check_in_to_exit': check_exit, 'total_dwell': dwell,
            'early_arrival': early, 'post_appointment_dwell': post,
            'facility_delay_flag': ('Facility-coded' if r.get('delay_cause') == 'Facility' else
                                    'Mixed cause' if r.get('delay_cause') == 'Mixed' else 'Not attributed') if valid else None,
            'counted': valid}


def analyze(visits):
    """Identity policy: source-record repeats are confirmed; identical content is suspected only."""
    results = [assess(r) for r in visits]
    # Resolve identity as a batch, not in encounter order. Only identical
    # source-record reimports and unambiguous human-confirmed links are excluded.
    # Conflicting source identities remain counted and require human review.
    def canonical(raw):
        return json.dumps(raw, sort_keys=True, default=str, separators=(',', ':'))

    def identity_key(record):
        raw = record['source']
        return (str(raw.get('visit_id') or ''), canonical(raw))

    by_id = defaultdict(list)
    by_source = defaultdict(list)
    by_fingerprint = defaultdict(list)
    for index, record in enumerate(results):
        raw = record['source']
        vid = raw.get('visit_id')
        if vid:
            by_id[vid].append(index)
        key = (raw.get('source_system'), raw.get('source_record_id'))
        if all(key):
            by_source[key].append(index)
        fp = (raw.get('facility_code'), raw.get('visit_type'),
              raw.get('arrival'), raw.get('check_in'), raw.get('exit'))
        by_fingerprint[fp].append(index)

    # A visit_id collision with different content is not proof of duplication.
    for indices in by_id.values():
        if len(indices) > 1 and len({canonical(results[i]['source']) for i in indices}) > 1:
            for i in indices:
                results[i]['warnings'].append('VISIT_ID_CONFLICT_REVIEW')

    for indices in by_source.values():
        if len(indices) < 2:
            continue
        # Compare observations, not import metadata such as local visit_id.
        def observation(i):
            return canonical({k: v for k, v in results[i]['source'].items()
                              if k not in ('visit_id', 'confirmed_duplicate_of')})
        if len({observation(i) for i in indices}) != 1:
            for i in indices:
                results[i]['warnings'].append('SOURCE_ID_CONFLICT_REVIEW')
            continue
        # Deterministic keeper; a source-record reimport is confirmed by
        # matching source identity AND matching observation content.
        keeper = min(indices, key=lambda i: identity_key(results[i]))
        for i in indices:
            if i != keeper:
                results[i]['warnings'].append('CONFIRMED_REIMPORT')
                results[i]['counted'] = False

    for i, record in enumerate(results):
        raw = record['source']
        target = raw.get('confirmed_duplicate_of')
        if not target:
            continue
        matches = by_id.get(target, [])
        # Reject ambiguous targets and cycles; never resolve by input position.
        source_id = raw.get('visit_id')
        if (len(matches) == 1 and target != source_id and
                results[matches[0]]['source'].get('confirmed_duplicate_of') != source_id):
            record['warnings'].append('HUMAN_CONFIRMED_DUPLICATE')
            record['counted'] = False
        else:
            record['warnings'].append('UNRESOLVED_DUPLICATE_REFERENCE')

    for indices in by_fingerprint.values():
        if len(indices) > 1:
            for i in indices:
                if results[i]['counted']:
                    results[i]['warnings'].append('SUSPECTED_DUPLICATE_REVIEW')
    groups = defaultdict(list)
    for r in results:
        if r['quality'] == 'VALID' and r['counted']:
            groups[(r['source']['facility_code'], r['source']['visit_type'])].append(r)
    summaries = {}
    for (facility, visit_type), rows in groups.items():
        def avg(name):
            vals = [v[name] for v in rows if v[name] is not None]
            return (sum(vals) / len(vals)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP) if vals else None
        eligible = [v for v in rows if v['appointment_eligible']]
        appointment_mean = ((sum(v['post_appointment_dwell'] for v in eligible) / len(eligible)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP) if eligible else None)
        summaries[(facility, visit_type)] = {
            'valid_visits': len(rows), 'mean_dwell': avg('total_dwell'),
            'mean_check_in_to_exit': avg('check_in_to_exit'),
            'mean_early_arrival': avg('early_arrival'),
            'appointment_eligible_visits': len(eligible), 'mean_post_appointment_dwell': appointment_mean,
            'max_dwell': max(v['total_dwell'] for v in rows),
            'facility_coded_delays': sum(v['source'].get('delay_cause') == 'Facility' for v in rows),
            'last_visit': max(v['source']['visit_date'] for v in rows)}
    return results, summaries
