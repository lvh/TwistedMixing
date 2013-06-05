from twisted.trial import unittest
from twisted.web import iweb, resource, server, wsgi
from twistyflask import chat, serve
from txsockjs import factory
from zope import interface

class ChildrenFirstResourceTests(unittest.TestCase):
    """
    Tests for the resource that delegates to children before
    delegating to a leaf.
    """
    def setUp(self):
        self.leaf = _FakeLeafResource()
        self.resource = serve.ChildrenFirstResource(self.leaf)

        self.child = resource.Resource()
        self.child.isLeaf = True
        self.resource.putChild("c", self.child)


    def test_getStaticChild(self):
        """
        When attempting to get a statically registered child resource, that
        child is returned.
        """
        request = _FakeRequest(["a", "b"], ["c", "d"])
        child = resource.getChildForRequest(self.resource, request)
        self.assertIdentical(child, self.child)
        self.assertEqual(request.prepath, ["a", "b", "c"])
        self.assertEqual(request.postpath, ["d"])


    def test_getChild(self):
        """
        When attempting to get a child resource that wasn't statically
        registered, the leaf is returned (which would have ``render``
        called on it).

        The request's prepath and postpath are unchanged, making the
        delegating resource "invisible".
        """
        request = _FakeRequest(["a", "b"], ["x", "y"])
        child = resource.getChildForRequest(self.resource, request)
        self.assertEqual(child, self.leaf)

        self.assertEqual(request.prepath, ["a", "b"])
        self.assertEqual(request.postpath, ["x", "y"])


    def test_render(self):
        """
        When rendering, the resource delegates to its leaf.
        """
        self.assertIdentical(self.leaf.request, None)
        request = _FakeRequest(["a", "b"], ["x", "y"])
        body = self.resource.render(request)
        self.assertEqual(body, "Hello from the leaf")
        self.assertIdentical(self.leaf.request, request)

        self.assertEqual(request.prepath, ["a", "b"])
        self.assertEqual(request.postpath, ["x", "y"])



@interface.implementer(iweb.IRequest)
class _FakeRequest(object):
    """
    A fake request with a prepath and a postpath.
    """
    def __init__(self, prepath, postpath):
        self.prepath = prepath
        self.postpath = postpath



@interface.implementer(resource.IResource)
class _FakeLeafResource(resource.Resource):
    """
    A fake leaf resource.
    """
    isLeaf = True

    def __init__(self):
        self.request = None
        resource.Resource.__init__(self)


    def render(self, request):
        self.request = request
        return "Hello from the leaf"


class BuildSiteTests(unittest.TestCase):
    """
    The ``buildSite`` function builds a site that serves both the Flask app
    and the SockJS endpoint.
    """
    def test_buildSite(self):
        request = _FakeRequest(["a", "b", "c"], ["x", "y", "z"])

        site = serve.buildSite()
        self.assertTrue(isinstance(site, server.Site))
        self.assertTrue(isinstance(site.resource, serve.ChildrenFirstResource))
        chatPage = site.resource.getChildWithDefault("chat", request)
        self.assertTrue(isinstance(chatPage, wsgi.WSGIResource))

        sockjsResource = site.resource.getChildWithDefault("sockjs", request)
        self.assertTrue(isinstance(sockjsResource, factory.SockJSResource))
        self.assertTrue(isinstance(sockjsResource._factory, chat.ChatFactory))
