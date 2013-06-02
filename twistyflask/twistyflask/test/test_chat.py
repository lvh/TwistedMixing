from json import dumps
from twisted.trial import unittest
from twistyflask import chat


class ChatFactoryTests(unittest.TestCase):
    """
    Tests for the chat factory.
    """
    def setUp(self):
        self.factory = chat.ChatFactory()


    def test_buildProtocol(self):
        """
        When asked to build a protocol, the factory instantiates a
        ``chat.ChatProtocol``, and assigns itself to its ``factory``
        attribute.
        """
        proto = self.factory.buildProtocol(None)
        self.assertTrue(isinstance(proto, chat.ChatProtocol))


    def test_emptyConnections(self):
        """
        A factory starts with an empty set of connections.
        """
        self.assertEqual(self.factory.connections, set())



class ChatProtocolTests(unittest.TestCase):
    """
    Tests for the chat protocol.
    """
    def setUp(self):
        self.factory = chat.ChatFactory()


    def test_name(self):
        """
        A new protocol's ``name`` attribute starts as ``None``.
        """
        proto = self.factory.buildProtocol(None)
        self.assertEqual(proto.name, None)


    def test_addRemoveFromFactory(self):
        """
        Protocols add themselves and then remove themselves again from
        their factory's collection of active connections when the
        connection is made and lost, respectively.
        """
        proto = self.factory.buildProtocol(None)
        self.assertNotIn(proto, self.factory.connections)
        proto.connectionMade()
        self.assertIn(proto, self.factory.connections)
        proto.connectionLost(None)
        self.assertNotIn(proto, self.factory.connections)


    def test_setName(self):
        """
        When the command to set the name is received, the name is set.
        """
        proto = self.factory.buildProtocol(None)
        command = {u"command": u"setName", u"name": u"\N{SNOWMAN}"}
        proto.dataReceived(dumps(command))
        self.assertEqual(proto.name, u"\N{SNOWMAN}")
