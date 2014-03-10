
"""
Facilitate profiling.

"""

import cStringIO as StringIO

import cherrypy
from tvb.interfaces.web.controllers.base_controller import BaseController

try:
    import yappi
    import yappi_stats

    class Yappi(object):
        exposed = True

        @cherrypy.expose
        def start(self):
            yappi.start()
            return '<a href="stats">stats</a>'

        @cherrypy.expose
        def stop(self):
            yappi.stop()
            return '<a href="stats">stats</a>'

        @cherrypy.expose
        def clear_stats(self):
            yappi.clear_stats()
            return '<a href="stats">stats</a>'

        @cherrypy.expose
        def stats(self):
            reload(yappi_stats)
            return yappi_stats.impl()

except ImportError:
    class Yappi(object):
        exposed = True
        @cherrypy.expose
        def start(self):
            return 'Yappi not available'


