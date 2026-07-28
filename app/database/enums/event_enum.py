import enum


class EventType(enum.Enum):
    """
    Event Type, includes possible conditions while calling the provider
    """

    CREATED = "CREATED"  # creation

    SUBMIT_ACCEPTED = "SUBMIT_ACCEPTED"  # submitting: first try
    SUBMIT_DUPLICATE_IGNORED = "SUBMIT_DUPLICATE_IGNORED"  # submitting: following tries, ignoring

    PROVIDER_CALL_ATTEMPTED = "PROVIDER_CALL_ATTEMPTED"  # every calling try
    PROVIDER_PAYMENT_ID_ASSIGNED = "PROVIDER_PAYMENT_ID_ASSIGNED"  # provider payment id saved (first try)
    PROVIDER_CALL_FAILED = "PROVIDER_CALL_FAILED"  # error while calling
    PROVIDER_LATE_RESPONSE_IGNORED = "PROVIDER_LATE_RESPONSE_IGNORED"  # provider late response

    RECOVERY_RESUMED = "RECOVERY_RESUMED"  # recover unfinished operations (in processing status) after app restart

    RECEIPT_APPLIED = "RECEIPT_APPLIED"  # first valid receipt (completed or rejected)
    RECEIPT_DUPLICATE_IGNORED = "RECEIPT_DUPLICATE_IGNORED"  # same late receipt (like first receipt)
    RECEIPT_CONFLICT_IGNORED = "RECEIPT_CONFLICT_IGNORED"  # opposite late receipt (ignoring)
    RECEIPT_PAYMENT_ID_MISMATCH = "RECEIPT_PAYMENT_ID_MISMATCH"  # payment id mismatch, conflict
