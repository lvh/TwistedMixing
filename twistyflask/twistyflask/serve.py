from txsockjs import factory
from twisted.application import internet, service
from twisted.internet import endpoints, reactor
from twisted.plugin import IPlugin
from twisted.python import usage
from twisted.web import wsgi, resource, server
from twistyflask import app, chat
from zope.interface import implementer

class ChildrenFirstResource(resource.Resource):
    """
    A resource that delegates to statically registered children before
    giving up and delegating to a given leaf resource.
    """
    def __init__(self, leaf):
        resource.Resource.__init__(self)
        self.leaf = leaf


    def getChild(self, child, request):
        """
        Reconstructs the request's postpath and prepath as if this
        resource wasn't there, then delegates to the leaf.

        This gets called when ``getChildWithDefault`` failed, i.e. we're
        handing it over to the leaf.
        """
        request.postpath.insert(0, request.prepath.pop())
        return self.leaf


    def render(self, request):
        """
        Delegates the requests to the leaf.
        """
        return self.leaf.render(request)



def buildSite():
    """
    Builds a site that will serve the WSGI app as well as the SockJS
    endpoint.
    """
    flaskResource = wsgi.WSGIResource(reactor, reactor.getThreadPool(), app)
    root = ChildrenFirstResource(flaskResource)
    root.putChild("sockjs", factory.SockJSResource(chat.ChatFactory()))
    return server.Site(root)



class Options(usage.Options):
    """
    Options for running the twistyflask demo.
    """
    optParameters = [
        ["endpoint", "e", "tcp:0", "The endpoint to listen on."],
    ]



@implementer(IPlugin, service.IServiceMaker)
class ServiceMaker(object):
    """
    Makes twistyflask demo services.
    """
    tapname = "twistyflask"
    description = 'A demo combining Twisted and Flask'
    options = Options

    _serverFromString = staticmethod(endpoints.serverFromString)
    _buildSite = staticmethod(buildSite)

    def makeService(self, options):
        """
        Makes a twistyflask demo service.
        """
        endpoint = self._serverFromString(reactor, options["endpoint"])
        factory = self._buildSite()
        return internet.StreamServerEndpointService(endpoint, factory)
