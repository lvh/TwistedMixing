from epsilon import extime
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
