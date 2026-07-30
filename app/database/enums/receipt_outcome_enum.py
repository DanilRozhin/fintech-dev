import enum


class ReceiptOutcome(enum.Enum):
    APPLIED = "APPLIED"
    MISMATCH = "MISMATCH"
    IGNORED = "IGNORED"
