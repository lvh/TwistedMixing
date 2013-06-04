from axiom import store
from json import dumps, loads
from twisted.test import proto_helpers
from twisted.trial import unittest
from twistyflask import app, chat, log


class ChatFactoryTests(unittest.TestCase):
    """
    Tests for the chat factory.
    """
    def setUp(self):
        app.store = store.Store()
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
        app.store = store.Store()
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


    def test_broadcast(self):
        """
        When a broadcast command is received, the message is broadcast to all
        active connections (including the sender). The message is also logged.
        """
        alice, bob, carol = [self._buildProtocol() for _ in xrange(3)]
        alice.name = u"\N{SNOWMAN}"

        message = u"\N{RADIOACTIVE SIGN}"
        command = {u"command": u"broadcast", u"message": message}
        alice.dataReceived(dumps(command))

        expected = {
            u"command": u"receive",
            u"message": message,
            u"sender": alice.name
        }
        for proto in [alice, bob, carol]:
            received = loads(proto.transport.value())
            self.assertEqual(received, expected)

        entry = app.store.findUnique(log.LogEntry)
        self.assertEqual(entry.sender, alice.name)
        self.assertEqual(entry.message, message)


    def _buildProtocol(self):
        """
        Builds a connected protocol with a string transport.
        """
        proto = self.factory.buildProtocol(None)
        proto.transport = proto_helpers.StringTransport()
        proto.connectionMade()
        return proto
