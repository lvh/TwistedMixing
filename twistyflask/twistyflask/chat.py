from json import dumps, loads
from twisted.internet import protocol


class ChatProtocol(protocol.Protocol):
    """
    A chat protocol, representing a single chat session.
    """
    def __init__(self):
        self.name = None


    def connectionMade(self):
        """
        Adds the chat session from the factory's open connections.
        """
        self.factory.connections.add(self)


    def connectionLost(self, reason):
        """
        Removes the chat session from the factory's open connections.
        """
        self.factory.connections.remove(self)


    def dataReceived(self, rawData):
        """
        Parses incoming data and dispatches to the appropriate method.
        """
        data = loads(rawData)
        handler = getattr(self, data.pop("command"))
        handler(**data)


    def setName(self, name):
        """
        Sets the name of the user in the current chat session.
        """
        self.name = name


    def broadcast(self, message):
        """
        Encodes a message receiving command with the given message and the
        sender's name, then sends it to all of the factory's connections.
        """
        command = dumps({
            u"command": u"receive",
            u"message": message,
            u"sender": self.name
        })

        for conn in self.factory.connections:
            conn.transport.write(command)



class ChatFactory(protocol.ServerFactory):
    """
    A chat factory with a single shared channel.
    """
    protocol = ChatProtocol

    def __init__(self):
        self.connections = set()
