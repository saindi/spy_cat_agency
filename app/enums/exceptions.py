from enum import StrEnum


class MessageException(StrEnum):
    object_not_found = "object_not_found"
    object_already_exists = "object_already_exists"
    gone = "gone"
    forbidden = "forbidden"
    bad_request = "bad_request"
