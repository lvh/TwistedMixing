import gevent
import time

import geventreactor
geventreactor.install()

from twisted.web import resource, server

class Clock(resource.Resource):
    isLeaf = True

    def __init__(self):
        resource.Resource.__init__(self)
        self.clock = time.clock()

    def increment(self):
        while True:
            gevent.sleep(1)
            self.clock = time.clock()
            print self.clock

    def render_GET(self, request):
        return "Clock: {}".format(self.clock)

from twisted.internet import reactor

clock = Clock()
gevent.Greenlet.spawn(clock.increment)
reactor.listenTCP(5000, server.Site(clock))

reactor.run()
