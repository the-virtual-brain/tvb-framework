# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

from functools import wraps
import json
import cherrypy
from genshi.template import TemplateLoader
import os
from tvb.basic.config.settings import TVBSettings as cfg, TVBSettings
from tvb.basic.logger.builder import get_logger
from tvb.core.services.settings_service import SettingsService
from tvb.interfaces.web.controllers import common


def settings():
    """
    Decorator to check if a the settings file exists before allowing access
    to some parts of TVB.
    """
    def dec(func):

        @wraps(func)
        def deco(*a, **b):
            if not SettingsService.is_first_run():
                return func(*a, **b)
            raise cherrypy.HTTPRedirect('/settings/settings')

        return deco
    return dec


def profile(template_path, func, *a, **b):
    """
    Wrapping function, used when profiling.
    We duplicate the code here, in a separate function, to help profiling,
    but for the runtime process we do not want a separate call, to increase time.
    """
    template_dict = func(*a, **b)
    ### Generate HTML given the path to the template and the data dictionary.
    loader = TemplateLoader()
    template = loader.load(template_path)
    stream = template.generate(**template_dict)
    return stream.render('xhtml')


def using_template(template_name):
    """
    Decorator to check if a user is logged before accessing a controller method.
    """
    template_path = os.path.join(cfg.TEMPLATE_ROOT, template_name + '.html')

    def dec(func):

        @wraps(func)
        def deco(*a, **b):
            try:
                ## Un-comment bellow for profiling each request:
                #import cherrypy.lib.profiler as profiler
                #p = profiler.Profiler("/Users/lia.domide/TVB/profiler/")
                #return p.run(profile, template_path, func, *a, **b)

                template_dict = func(*a, **b)
                if not cfg.RENDER_HTML:
                    return template_dict
                    ### Generate HTML given the path to the template and the data dictionary.
                loader = TemplateLoader()
                template = loader.load(template_path)
                stream = template.generate(**template_dict)
                return stream.render('xhtml')
            except Exception, excep:
                if isinstance(excep, cherrypy.HTTPRedirect):
                    raise
                get_logger("tvb.interface.web.controllers.base_controller").exception(excep)
                common.set_error_message("An unexpected exception appeared. Please contact your system administrator.")
                raise cherrypy.HTTPRedirect("/tvb?error=True")

        return deco
    return dec


def ajax_call(json_form=True):
    """
    Decorator to wrap all JSON calls, and log on server in case of an exception.
    """
    def dec(func):

        @wraps(func)
        def deco(*a, **b):
            try:
                result = func(*a, **b)
                if json_form:
                    return json.dumps(result)
                return result

            except Exception, excep:
                if isinstance(excep, cherrypy.HTTPRedirect):
                    raise
                logger = get_logger("tvb.interface.web.controllers.base_controller")
                logger.error("Encountered exception when calling asynchronously :" + str(func))
                logger.exception(excep)
                raise

        return deco
    return dec


def logged():
    """
    Decorator to check if a user is logged before accessing a controller method.
    """
    def dec(func):

        @wraps(func)
        def deco(*a, **b):
            if hasattr(cherrypy, common.KEY_SESSION):
                if common.get_logged_user():
                    return func(*a, **b)

            common.set_error_message('Login Required!')
            raise cherrypy.HTTPRedirect('/user')

        return deco
    return dec


def admin():
    """
    Decorator to check if a user is administrator before accessing a controller method
    """
    def dec(func):

        @wraps(func)
        def deco(*a, **b):
            if hasattr(cherrypy, common.KEY_SESSION):
                user = common.get_logged_user()
                if (user is not None and user.is_administrator()) or SettingsService.is_first_run():
                    return func(*a, **b)
            common.set_error_message('Only Administrators can access this application area!')
            raise cherrypy.HTTPRedirect('/tvb')

        return deco
    return dec


def context_selected():
    """
    Decorator to check if a project is currently selected.
    """
    def dec(func):

        @wraps(func)
        def deco(*a, **b):
            if hasattr(cherrypy, common.KEY_SESSION):
                if common.KEY_PROJECT in cherrypy.session:
                    return func(*a, **b)
            common.set_error_message('You should first select a Project!')
            raise cherrypy.HTTPRedirect('/project/viewall')

        return deco
    return dec