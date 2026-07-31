import enum


class TriggerType(enum.Enum):
    SUBMIT = "SUBMIT"
    RETRY = "RETRY"
    RECOVERY = "RECOVERY"
