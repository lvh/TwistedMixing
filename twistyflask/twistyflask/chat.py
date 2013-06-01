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



class ChatFactory(protocol.ServerFactory):
    """
    A chat factory with a single shared channel.
    """
    protocol = ChatProtocol

    def __init__(self):
        self.connections = set()
