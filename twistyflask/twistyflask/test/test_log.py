from axiom import store
from epsilon import extime
from twisted.internet import threads
from twisted.trial import unittest
from twistyflask import log

class LogEntryTests(unittest.TestCase):
    def test_time(self):
        """
        New entries get timestamped automatically.
        """
        entry = log.LogEntry(sender=u"s", message=u"m")
        delta = (extime.Time() - entry.time).total_seconds()
        self.assertTrue(delta < 0.1)


class GetLogEntriesTests(unittest.TestCase):
    """
    Getting log entries works from a non-reactor thread.
    """
    def setUp(self):
        """
        Creates some log entries.
        """
        self.store = s = store.Store()
        self.first = log.LogEntry(store=s, sender=u"A", message=u"X")
        self.second = log.LogEntry(store=s, sender=u"B", message=u"Y")


    def _getEntriesTest(self):
        """
        A generic entry getting test.

        This test is intentionally agnostic about which thread it is ran in.
        Run it from different threads in different test methods.
        """
        first, second = log.getLogEntries(self.store)
        self.assertIdentical(first, self.first)
        self.assertIdentical(second, self.second)


    def test_fromReactorThread(self):
        """
        Getting log entries works from the reactor thread.
        """
        self._getEntriesTest()


    def test_fromOtherThread(self):
        """
        Getting log entries works from another thread.
        """
        return threads.deferToThread(self._getEntriesTest)
