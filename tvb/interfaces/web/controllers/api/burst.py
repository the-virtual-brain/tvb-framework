
"""
Providing the Burst services as an HTTP/JSON API.

"""

import json
import cherrypy
import tvb.interfaces.web.controllers.basecontroller as base
from tvb.core.services.burstservice import BurstService

# simulator imports 
from tvb.datatypes import connectivity, equations, surfaces, patterns
from tvb.simulator import noise, integrators, models, coupling, monitors, simulator

import tvb.interfaces.web.controllers.api.burst_impl as impl

class BurstAPIController(base.BaseController):
    """
    Provides an HTTP/JSON API to the simulator/burst mechanics
    reusing a BurstController where necessary.

    """

    exposed = True

    def __init__(self):
        super(BurstAPIController, self).__init__()
        self.burst_service = BurstService()

    @cherrypy.expose
    def index(self):

        reload(impl)
        return impl.index(self)

    @cherrypy.expose
    def read(self, pid):
        """
        Get information on existing burst operations

        """

        reload(impl)
        return impl.read(self, pid)

    @cherrypy.expose
    def dir(self):
        """
        Query existing classes in TVB

        """

        info = {}

        for m in [models, coupling, integrators, noise, monitors, connectivity, equations, surfaces, patterns]:
            minfo = {}
            for k in dir(m):
                v = getattr(m, k)
                if isinstance(v, type):
                    minfo[k] = k + '\n\n' + getattr(v, '__doc__', k)
            info[m.__name__.split('.')[-1]] = minfo

        return json.dumps(info)

    @cherrypy.expose
    def create(self, opt):
        """
        Create a new simulation/burst

        """

        reload(impl)
        return impl.create(self, opt)


