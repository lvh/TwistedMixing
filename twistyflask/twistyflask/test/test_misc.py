"""
Tests for miscellaneous stuff like app setup.
"""
from twisted.trial import unittest
from twisted.python import filepath
from twistyflask import addStore, app

class AppSetupTests(unittest.TestCase):
    def test_has_in_memory_store(self):
        """
        If the STORE_PATH env var is unset, the app gets an in-memory store.
        """
        addStore(_environ={})
        self.assertEqual(app.store.dbdir, None)


    def test_has_on_disk_store(self):
        """
        If the STORE_PATH env var is set, the app gets a store with that path.
        """
        storePath = self.mktemp()
        addStore(_environ={"STORE_PATH": storePath})
        self.assertEqual(app.store.dbdir, filepath.FilePath(storePath))
