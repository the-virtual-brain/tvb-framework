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

"""
The Main class in this file is initialized in web/run.py to be 
served on the root of the Web site.

This is the main UI entry point.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

import os
import json
import cherrypy
from copy import copy
from genshi.template.loader import TemplateLoader
from tvb.config import CONNECTIVITY_CLASS, CONNECTIVITY_MODULE
from tvb.basic.config.settings import TVBSettings as cfg
from tvb.basic.logger.builder import get_logger
from tvb.core.services.settings_service import SettingsService
from tvb.core.services.user_service import UserService
from tvb.core.services.flow_service import FlowService
from tvb.interfaces.web.structure import WebStructure
from functools import wraps

#These are global constants, used for session attributes and template variables.
#Message, Current Project and User values are stored in session, because they 
# need to be translated between multiple pages.
#The rest of the values are stored in the template dictionary.
TYPE_ERROR = "ERROR"
TYPE_WARNING = "WARNING"
TYPE_INFO = "INFO"

KEY_CURRENT_VERSION = "currentVersion"
KEY_SESSION = "session"
KEY_SESSION_TREE = "treeSessionKey"
KEY_USER = "user"
KEY_SHOW_ONLINE_HELP = "showOnlineHelp"
KEY_MESSAGE = "message"
KEY_MESSAGE_TYPE = "messageType"
KEY_PROJECT = "selectedProject"
KEY_ERRORS = "errors"
KEY_FORM_DATA = "data"
KEY_PARAMETERS_CONFIG = "param_checkbox_config"
KEY_FIRST_RUN = "first_run"
KEY_LINK_ANALYZE = "analyzeCategoryLink"
KEY_LINK_CONNECTIVITY_TAB = "connectivityTabLink"
KEY_TITLE = "title"
KEY_ADAPTER = "currentAlgoId"
KEY_OPERATION_ID = "currentOperationId"
KEY_SECTION = "section_name"
KEY_SUB_SECTION = 'subsection_name'
KEY_INCLUDE_RESOURCES = 'includedResources'
KEY_SUBMENU_LIST = 'submenu_list'
KEY_SUBMIT_LINK = 'submitLink'
KEY_DISPLAY_MENU = "displayControl"
KEY_PARENT_DIV = "parent_div"
#User section and settings section specific
KEY_IS_RESTART = "tvbRestarted"
KEY_INCLUDE_TOOLTIP = "includeTooltip"
KEY_WRAP_CONTENT_IN_MAIN_DIV = "wrapContentInMainDiv"
KEY_CURRENT_TAB = "currentTab"

KEY_BURST_CONFIG = 'burst_configuration'
KEY_CACHED_SIMULATOR_TREE = 'simulator_input_tree'
KEY_BACK_PAGE = "back_page_link"
KEY_SECTION_TITLES = "section_titles"
KEY_SUBSECTION_TITLES = "sub_section_titles"

# Overlay specific keys
KEY_OVERLAY_TITLE = "overlay_title"
KEY_OVERLAY_DESCRIPTION = "overlay_description"
KEY_OVERLAY_CLASS = "overlay_class"
KEY_OVERLAY_CONTENT_TEMPLATE = "overlay_content_template"
KEY_OVERLAY_TABS = "overlay_tabs"
KEY_OVERLAY_INDEXES = "overlay_indexes"
KEY_OVERLAY_PAGINATION = "show_overlay_pagination"
KEY_OVERLAY_PREVIOUS = "action_overlay_previous"
KEY_OVERLAY_NEXT = "action_overlay_next"



def settings():
    """
    Annotation to check if a the settings file exists before allowing access
    to some parts of TVB.
    """


    def dec(func):
        """ Annotation wrapping web public function"""


        def deco(*a, **b):
            """ Decorator for public method"""
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
    Annotation to check if a user is logged before accessing a controller method.
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
                set_error_message("An unexpected exception appeared. Please contact your system administrator.")
                raise cherrypy.HTTPRedirect("/tvb?error=True")

        return deco
    return dec



def ajax_call(json_form=True):
    """
    Annotation to wrap all JSON calls, and log on server in case of an exception.
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



def set_message(msg, m_type):
    """ Set in session a message of a given type"""
    cherrypy.session.acquire_lock()
    cherrypy.session[KEY_MESSAGE] = msg
    cherrypy.session[KEY_MESSAGE_TYPE] = m_type
    cherrypy.session.release_lock()



def set_error_message(msg):
    """ Set error message in session"""
    set_message(msg, TYPE_ERROR)



def set_warning_message(msg):
    """ Set warning message in session"""
    set_message(msg, TYPE_WARNING)



def set_info_message(msg):
    """ Set info message in session"""
    set_message(msg, TYPE_INFO)



def get_from_session(attribute):
    """ check if something exists in session and return"""
    return cherrypy.session.get(attribute)



def get_current_project():
    """Get current Project from session"""
    return get_from_session(KEY_PROJECT)



def get_logged_user():
    """Get current logged User from session"""
    return get_from_session(KEY_USER)



def add2session(key, value):
    """ Set in session, at a key, a value"""
    cherrypy.session.acquire_lock()
    cherrypy.session[key] = value
    cherrypy.session.release_lock()



def remove_from_session(key):
    """ Remove from session an attributes if exists."""
    cherrypy.session.acquire_lock()
    if key in cherrypy.session:
        result = copy(cherrypy.session[key])
        del cherrypy.session[key]
        cherrypy.session.release_lock()
        return result
    cherrypy.session.release_lock()
    return None


# Constants used be the mechanism that deletes files on disk
FILES_TO_DELETE_ATTR = "files_to_delete"



class BaseController(object):
    """
    This class contains the methods served at the root of the Web site.
    """


    def __init__(self):
        self.logger = get_logger(self.__class__.__module__)
        self.version_info = None

        self.user_service = UserService()
        self.flow_service = FlowService()

        analyze_category = self.flow_service.get_launchable_non_viewers()
        self.analyze_category_link = '/flow/step/' + str(analyze_category.id)
        self.analyze_adapters = None

        self.connectivity_tab_link = '/flow/step_connectivity'
        view_category = self.flow_service.get_visualisers_category()
        conn_id = self.flow_service.get_algorithm_by_module_and_class(CONNECTIVITY_MODULE, CONNECTIVITY_CLASS)[1].id
        connectivity_link = self.get_url_adapter(view_category.id, conn_id)

        local_connectivity_link = '/spatial/localconnectivity/step_1/1'

        connectivity_submenu = [dict(title="Large Scale Connectivity", subsection="connectivity",
                                     description="View Connectivity Regions. Perform Connectivity lesions",
                                     link=connectivity_link),
                                dict(title="Local Connectivity", subsection="local", link=local_connectivity_link,
                                     description="Create or view existent Local Connectivity entities.")]
        self.connectivity_submenu = connectivity_submenu


    @staticmethod
    def mark_file_for_delete(file_name, delete_parent_folder=False):
        """
        This method stores provided file name in session, 
        and later on when request is done, all these files/folders
        are deleted
        
        :param file_name: name of the file or folder to be deleted
        :param delete_parent_folder: specify if the parent folder of the file should be removed too.
        """
        # No processing if no file specified
        if file_name is None:
            return

        files_list = get_from_session(FILES_TO_DELETE_ATTR)
        if files_list is None:
            files_list = []
            add2session(FILES_TO_DELETE_ATTR, files_list)

        # Now add file/folder to list
        if delete_parent_folder:
            folder_name = os.path.split(file_name)[0]
            files_list.append(folder_name)
        else:
            files_list.append(file_name)


    def _mark_selected(self, project):
        """
        Set the project passed as parameter as the selected project.
        """
        previous_project = get_current_project()
        ### Update project stored in selection, with latest Project entity from DB.
        members = self.user_service.get_users_for_project("", project.id)[1]
        project.members = members
        remove_from_session(KEY_CACHED_SIMULATOR_TREE)
        add2session(KEY_PROJECT, project)

        if previous_project is None or previous_project.id != project.id:
            ### Clean Burst selection from session in case of a different project.
            remove_from_session(KEY_BURST_CONFIG)
            ### Store in DB new project selection
            user = get_from_session(KEY_USER)
            if user is not None:
                self.user_service.save_project_to_user(user.id, project.id)
            ### Display info message about project change
            self.logger.debug("Selected project is now " + project.name)
            set_info_message("Your current working project is: " + str(project.name))


    @staticmethod
    def get_url_adapter(step_key, adapter_id, back_page=None):
        """
        Compute the URLs for a given adapter. 
        Same URL is used both for GET and POST.
        """
        result_url = '/flow/' + str(step_key) + '/' + str(adapter_id)
        if back_page is not None:
            result_url = result_url + "?back_page=" + str(back_page)
        return result_url


    @cherrypy.expose
    def index(self):
        """
        / Path response
        Redirects to /tvb
        """
        raise cherrypy.HTTPRedirect('/user')


    @cherrypy.expose()
    @using_template('user/base_user')
    def tvb(self, error=False, **data):
        """
        /tvb URL
        Returns the home page with the messages stored in the user's session.
        """
        self.logger.debug("Unused submit attributes:" + str(data))
        template_dictionary = dict(mainContent="../index", title="The Virtual Brain Project")
        template_dictionary = self._fill_user_specific_attributes(template_dictionary)
        if get_from_session(KEY_IS_RESTART):
            template_dictionary[KEY_IS_RESTART] = True
            remove_from_session(KEY_IS_RESTART)
        return self.fill_default_attributes(template_dictionary, error)


    @cherrypy.expose
    @using_template('user/base_user')
    def error(self, **data):
        """Error page to redirect when something extremely bad happened"""
        template_specification = dict(mainContent="../error", title="Error page", data=data)
        template_specification = self._fill_user_specific_attributes(template_specification)
        return self.fill_default_attributes(template_specification)


    def _populate_user_and_project(self, template_dictionary, escape_db_operations=False):
        """
         Populate the template dictionary with current logged user (from session).
         """
        logged_user = get_logged_user()
        template_dictionary[KEY_USER] = logged_user
        show_help = logged_user is not None and logged_user.is_online_help_active()
        template_dictionary[KEY_SHOW_ONLINE_HELP] = show_help

        project = get_current_project()
        template_dictionary[KEY_PROJECT] = project
        if project is not None and not escape_db_operations:
            self.update_operations_count()
        return template_dictionary


    @staticmethod
    def _populate_message(template_dictionary):
        """
         Populate the template dictionary with current message stored in session. 
         Also specify the message type (default INFO).
         Clear from session current message (to avoid displaying it twice).
         """
        message_type = remove_from_session(KEY_MESSAGE_TYPE)
        if message_type is None:
            message_type = TYPE_INFO
        template_dictionary[KEY_MESSAGE_TYPE] = message_type

        message = remove_from_session(KEY_MESSAGE)
        if message is None:
            message = ""
        template_dictionary[KEY_MESSAGE] = message
        return template_dictionary


    def _populate_menu(self, template_dictionary):
        """
        Populate current template with information for the Left Menu.
        """
        if KEY_FIRST_RUN not in template_dictionary:
            template_dictionary[KEY_FIRST_RUN] = False
        template_dictionary[KEY_LINK_ANALYZE] = self.analyze_category_link
        template_dictionary[KEY_LINK_CONNECTIVITY_TAB] = self.connectivity_tab_link
        if KEY_BACK_PAGE not in template_dictionary:
            template_dictionary[KEY_BACK_PAGE] = False
        template_dictionary[KEY_SECTION_TITLES] = WebStructure.WEB_SECTION_TITLES
        template_dictionary[KEY_SUBSECTION_TITLES] = WebStructure.WEB_SUBSECTION_TITLES
        return template_dictionary


    def _populate_section(self, algo_group, result_template):
        """
        Populate Section and Sub-Section fields from current Algorithm-Group.
        """
        if algo_group.module == CONNECTIVITY_MODULE:
            result_template[KEY_SECTION] = 'connectivity'
            result_template[KEY_SUB_SECTION] = 'connectivity'
            result_template[KEY_SUBMENU_LIST] = self.connectivity_submenu
        elif algo_group.group_category.display:
            ### Visualizers on the Burst Page
            result_template[KEY_SECTION] = 'burst'
            result_template[KEY_SUB_SECTION] = 'view_' + algo_group.subsection_name

        elif algo_group.group_category.rawinput:
            ### Upload algorithms
            result_template[KEY_SECTION] = 'project'
            result_template[KEY_SUB_SECTION] = 'data'
        elif 'RAW_DATA' in algo_group.group_category.defaultdatastate:
            ### Creators
            result_template[KEY_SECTION] = 'stimulus'
            result_template[KEY_SUB_SECTION] = 'stimulus'
        else:
            ### Analyzers
            result_template[KEY_SECTION] = algo_group.group_category.displayname.lower()
            result_template[KEY_SUB_SECTION] = algo_group.subsection_name
            result_template[KEY_SUBMENU_LIST] = self.analyze_adapters


    def _fill_user_specific_attributes(self, template_dictionary):
        """
        Attributes needed for base_user template.
        """
        template_dictionary[KEY_INCLUDE_TOOLTIP] = False
        template_dictionary[KEY_WRAP_CONTENT_IN_MAIN_DIV] = True
        template_dictionary[KEY_CURRENT_TAB] = 'none'

        return template_dictionary


    def fill_default_attributes(self, template_dictionary, escape_db_operations=False):
        """
        Fill into 'template_dictionary' data that we want to have ready in UI.
        """
        template_dictionary = self._populate_user_and_project(template_dictionary, escape_db_operations)
        template_dictionary = self._populate_message(template_dictionary)
        template_dictionary = self._populate_menu(template_dictionary)

        if KEY_ERRORS not in template_dictionary:
            template_dictionary[KEY_ERRORS] = {}
        if KEY_FORM_DATA not in template_dictionary:
            template_dictionary[KEY_FORM_DATA] = {}
        if KEY_SUB_SECTION not in template_dictionary and KEY_SECTION in template_dictionary:
            template_dictionary[KEY_SUB_SECTION] = template_dictionary[KEY_SECTION]
        if KEY_SUBMENU_LIST not in template_dictionary:
            template_dictionary[KEY_SUBMENU_LIST] = None

        template_dictionary[KEY_CURRENT_VERSION] = cfg.BASE_VERSION
        return template_dictionary


    def fill_overlay_attributes(self, template_dictionary, title, description, content_template,
                                css_class, tabs=None, overlay_indexes=None):
        """
        This method prepares parameters for rendering overlay (overlay.html)
        
        :param title: overlay title
        :param description: overlay description
        :param content_template: path&name of the template file which will fill overlay content (without .html)
        :param css_class: CSS class to be applied on overlay 
        :param tabs: list of strings containing names of the tabs 
        """
        if template_dictionary is None:
            template_dictionary = dict()

        template_dictionary[KEY_OVERLAY_TITLE] = title
        template_dictionary[KEY_OVERLAY_DESCRIPTION] = description
        template_dictionary[KEY_OVERLAY_CONTENT_TEMPLATE] = content_template
        template_dictionary[KEY_OVERLAY_CLASS] = css_class
        template_dictionary[KEY_OVERLAY_TABS] = tabs if tabs is not None and len(tabs) > 0 else []
        if overlay_indexes is not None:
            template_dictionary[KEY_OVERLAY_INDEXES] = overlay_indexes
        else:
            template_dictionary[KEY_OVERLAY_INDEXES] = range(len(tabs)) if tabs is not None else []
        template_dictionary[KEY_OVERLAY_PAGINATION] = False

        return template_dictionary


    @cherrypy.expose
    @using_template('overlay_blocker')
    def showBlockerOverlay(self, **data):
        """
        Returns the content of the blocking overlay (covers entire page and do not allow any action)
        """
        return self.fill_default_attributes(dict(data))
    
    
    def update_operations_count(self):
        """
        If a project is selected, update Operation Numbers in call-out.
        """
        project = get_current_project()
        if project is not None:
            fns, sta, err, canceled = self.flow_service.get_operation_numbers(project.id)
            project.operations_finished = fns
            project.operations_started = sta
            project.operations_error = err
            project.operations_canceled = canceled
            add2session(KEY_PROJECT, project)
            
                    
            
            
            