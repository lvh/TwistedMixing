from axiom import attributes, item
from epsilon import extime

class LogEntry(item.Item):
    """
    A chat channel log entry.
    """
    time = attributes.timestamp(defaultFactory=extime.Time)
    sender = attributes.text(allowNone=False)
    message = attributes.text(allowNone=False)
