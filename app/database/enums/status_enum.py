import enum


class StatusType(enum.Enum):
    """
    Status Type, includes created, processing, completed, rejected values
    """

    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
