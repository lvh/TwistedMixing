from axiom import attributes, item
from epsilon import extime
from twisted.internet import reactor, threads
from twisted.python import threadable
from twistyflask import app

class LogEntry(item.Item):
    """
    A chat channel log entry.
    """
    time = attributes.timestamp(defaultFactory=extime.Time)
    sender = attributes.text(allowNone=False)
    message = attributes.text(allowNone=False)


def getLogEntries(store=None, _reactor=reactor):
    """
    Gets log entries.

    This actually makes a blocking call to ``_getLogEntries``.
    """
    store = store or app.store # Don't bind at function creation, for testing
    if threadable.isInIOThread():
        return _getLogEntries(store)
    else:
        return threads.blockingCallFromThread(_reactor, _getLogEntries, store)


def _getLogEntries(store):
    """
    Really get log entries.

    Must be called from the thread that produced the SQLite connection of the
    app's store. Generally, that's the reactor thread.
    """
    return store.query(LogEntry, sort=LogEntry.time.ascending)
