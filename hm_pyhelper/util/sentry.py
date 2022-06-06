from typing import Dict, Union
import hashlib

EVENT_COUNT_KEY = "event_count"
SUPPRESSION_COUNT_KEY = "suppression_count"

# per session event counters, didn't feel the need to persist them
event_counters = {}

# maximum suppression interval. It grows exponentially till this value is reached.
max_suppression_count = 128


def sentry_fingerprint(hints: Dict) -> Union[str, None]:
    """ return sha256 of log_record/exc_info as fingerprint"""
    fingerprint_info_key = 'log_record'
    if 'exc_info' in hints:
        fingerprint_info_key = 'exc_info'

    value_to_fingerprint = hints.get(fingerprint_info_key, None)

    if not value_to_fingerprint:
        return None

    # using sha256 only to get a consistent length fingerprint
    # if it is deemed a performance issue, we can replace it with
    # with a truncated string as well
    fingerprint_bytes = str(value_to_fingerprint).encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(fingerprint_bytes)
    fingerprint = sha256_hash.hexdigest()

    return fingerprint


def process_fingerprint(fingerprint: str) -> bool:
    """
    does book keeping based on event fingerprint.
    returns true if the event should be allowed to propagate
    """
    # decide whether to send or suppress
    send_event = False
    if fingerprint in event_counters:
        event_count = event_counters[fingerprint][EVENT_COUNT_KEY]
        suppression_count = event_counters[fingerprint][SUPPRESSION_COUNT_KEY]
        event_count += 1
        if event_count % suppression_count == 0:
            send_event = True
            suppression_count = min(suppression_count*2, max_suppression_count)
        event_counters[fingerprint] = {
            EVENT_COUNT_KEY: event_count,
            SUPPRESSION_COUNT_KEY:  suppression_count
        }
    else:
        event_counters[fingerprint] = {
            EVENT_COUNT_KEY: 1,
            SUPPRESSION_COUNT_KEY:  1
            }
        send_event = True

    return send_event


def before_send_filter(event: Dict, hints: Dict) -> Union[Dict, None]:
    """
    Event filter function for sentry_sdk_init() to be passed as its before_send argument.
    It will suppress logging events exponentially till max_suppression_count is reached.
    eg. 1, 2, 4, 8, 16, 32, 64 ....  max_suppression_count
    event instance count in this series will be passed to sentry and rest will be
    dropped.
    When an event is allowed to pass through to sentry, it will be enriched it with
    current event count for that unique event which is determined by its fingerprint
    calculated with sentry_fingerprint().
    One can find the event_count in event data @ event["extra"][event_count]

    Returns:
        event: if event is allowed to propagate
        None: if event is dropped.
    """
    # process all uncaught exceptions
    if 'exception' in event:
        return event

    # if no hints, no filtering - logging and exception events will have hints.
    if not hints:
        return event

    fingerprint = sentry_fingerprint(hints)
    if not fingerprint:
        return event

    send_event = process_fingerprint(fingerprint)
    if send_event:
        event["extra"][EVENT_COUNT_KEY] = event_counters[fingerprint][EVENT_COUNT_KEY]
        return event
    else:
        return None
