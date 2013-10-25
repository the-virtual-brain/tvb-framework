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
Here, user related tasks are described.
Basic authentication processes are described here, 
but also user related annotation (checked-logged).

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""
import cherrypy
import formencode
from hashlib import md5
from urllib2 import urlopen
from formencode import validators
from tvb.basic.config.settings import TVBSettings as cfg
from tvb.core.services.user_service import UserService, KEY_PASSWORD, KEY_EMAIL, KEY_USERNAME, KEY_COMMENT
from tvb.core.services.project_service import ProjectService
from tvb.core.services.exceptions import UsernameException
from tvb.core.services.settings_service import SettingsService
from tvb.interfaces.web.controllers.base_controller import using_template, ajax_call, settings
import tvb.interfaces.web.controllers.base_controller as basecontroller
from functools import wraps

KEY_SERVER_VERSION = "versionInfo"
KEY_CURRENT_VERSION_FULL = "currentVersionLongText"
KEY_NEED_FILE_STORAGE_UPG = "needFileStorageUpgrade"


def logged():
    """
    Annotation to check if a user is logged before accessing a controller method.
    """

    def dec(func):
        @wraps(func)
        def deco(*a, **b):            
            if hasattr(cherrypy, basecontroller.KEY_SESSION):
                if basecontroller.get_logged_user():
                    return func(*a, **b)

            basecontroller.set_error_message('Login Required!')
            raise cherrypy.HTTPRedirect('/user')

        return deco

    return dec


def admin():
    """
    Annotation to check if a user is administrator before accessing a controller method
    """

    def dec(func):
        """ Annotation wrapping web public function"""

        def deco(*a, **b):
            """ Decorator for public method"""
            if hasattr(cherrypy, basecontroller.KEY_SESSION):
                user = basecontroller.get_logged_user()
                if (user is not None and user.is_administrator()) or SettingsService.is_first_run():
                    return func(*a, **b)
            basecontroller.set_error_message('Only Administrators can access this application area!')
            raise cherrypy.HTTPRedirect('/tvb')

        return deco

    return dec


class UserController(basecontroller.BaseController):
    """
    This class takes care of the user authentication and/or register.
    """

    def __init__(self):
        basecontroller.BaseController.__init__(self)


    @cherrypy.expose
    @using_template('user/base_user')
    @settings()
    def index(self, **data):
        """
        Login page (with or without messages).
        """
        template_specification = dict(mainContent="login", title="Login", data=data)
        if cherrypy.request.method == 'POST':
            form = LoginForm()
            try:
                data = form.to_python(data)
                username = data[KEY_USERNAME]
                password = data[KEY_PASSWORD]
                user = self.user_service.check_login(username, password)
                if user is not None:
                    basecontroller.add2session(basecontroller.KEY_USER, user)
                    basecontroller.set_info_message('Welcome ' + username)
                    self.logger.debug("User " + username + " has just logged in!")
                    if user.selected_project is not None:
                        prj = user.selected_project
                        prj = ProjectService().find_project(prj)
                        self._mark_selected(prj)
                    raise cherrypy.HTTPRedirect('/user/profile')
                else:
                    basecontroller.set_error_message('Wrong username/password, or user not yet validated...')
                    self.logger.debug("Wrong username " + username + " !!!")
            except formencode.Invalid, excep:
                template_specification[basecontroller.KEY_ERRORS] = excep.unpack_errors()

        return self.fill_default_attributes(template_specification)


    @cherrypy.expose
    @using_template('user/base_user')
    @settings()
    @logged()
    def profile(self, logout=False, save=False, **data):
        """
        Display current user's profile page.
        On POST: logout, or save password/email.
        """
        if cherrypy.request.method == 'POST' and logout:
            raise cherrypy.HTTPRedirect('/user/logout')
        template_specification = dict(mainContent="profile", title="User Profile")
        if cherrypy.request.method == 'POST' and save:
            try:
                form = EditUserForm()
                data = form.to_python(data)
                user = basecontroller.get_logged_user()
                if KEY_PASSWORD in data and data[KEY_PASSWORD]:
                    user.password = md5(data[KEY_PASSWORD]).hexdigest()
                if KEY_EMAIL in data and data[KEY_EMAIL]:
                    user.email = data[KEY_EMAIL]
                old_password = None
                if 'old_password' in data and data['old_password']:
                    old_password = md5(data['old_password']).hexdigest()
                self.user_service.edit_user(user, old_password)
                if old_password:
                    basecontroller.set_info_message("Changes Submitted!")
                else:
                    basecontroller.set_info_message("Submitted!  No password changed.")
            except formencode.Invalid, excep:
                template_specification[basecontroller.KEY_ERRORS] = excep.unpack_errors()
            except UsernameException, excep:
                self.logger.exception(excep)
                user = basecontroller.get_logged_user()
                basecontroller.add2session(basecontroller.KEY_USER, self.user_service.get_user_by_id(user.id))
                basecontroller.set_error_message("Could not save changes. Probably wrong old password!!")
        else:
            user = basecontroller.get_logged_user()
            #Update session user since disk size might have changed from last time to profile.
            user = self.user_service.get_user_by_id(user.id)
            basecontroller.add2session(basecontroller.KEY_USER, user)
        return self.fill_default_attributes(template_specification)


    @cherrypy.expose
    @ajax_call()
    @logged()
    def logout(self):
        """
        Logging out user and clean session
        """
        user = basecontroller.remove_from_session(basecontroller.KEY_USER)
        if user is not None:
            self.logger.debug("User " + user.username + " is just logging out!")
        basecontroller.remove_from_session(basecontroller.KEY_PROJECT)
        basecontroller.remove_from_session(basecontroller.KEY_BURST_CONFIG)
        basecontroller.remove_from_session(basecontroller.KEY_CACHED_SIMULATOR_TREE)
        basecontroller.set_info_message("Thank you for using The Virtual Brain!")
        raise cherrypy.HTTPRedirect("/user")


    @cherrypy.expose
    @ajax_call()
    @logged()
    def switchOnlineHelp(self):
        """
        Switch flag that displays online helps
        """
        user = basecontroller.get_logged_user()

        # Change OnlineHelp Active flag and save user
        user.switch_online_help_state()
        self.user_service.edit_user(user)
        raise cherrypy.HTTPRedirect("/user/profile")


    @cherrypy.expose
    @using_template('user/base_user')
    def register(self, cancel=False, **data):
        """
        This register form send an e-mail to the user and to the site admin.
        """
        template_specification = dict(mainContent="register", title="Register", data=data)
        redirect = False
        if cherrypy.request.method == 'POST':
            if cancel:
                raise cherrypy.HTTPRedirect('/user')
            try:
                okmessage = self._create_user(**data)
                basecontroller.set_info_message(okmessage)
                redirect = True
            except formencode.Invalid, excep:
                template_specification[basecontroller.KEY_ERRORS] = excep.unpack_errors()
                redirect = False
            except Exception, excep1:
                self.logger.error("Could not create user:" + data["username"])
                self.logger.exception(excep1)
                basecontroller.set_error_message("We are very sorry, but we could not create your " +
                                                 "user. Most probably is because it was impossible" +
                                                 " to sent emails. Please try again later...")
                redirect = False

        if redirect:
            #Redirect to login page, with some success message to display
            raise cherrypy.HTTPRedirect('/user')
        else:
            #Stay on the same page
            return self.fill_default_attributes(template_specification)


    @cherrypy.expose
    @using_template('user/base_user')
    def create_new(self, cancel=False, **data):
        """
        Create new user with data submitted from UI.
        """
        if cancel:
            raise cherrypy.HTTPRedirect('/user/usermanagement')
        template_specification = dict(mainContent="create_new", title="Create New", data=data)
        redirect = False
        if cherrypy.request.method == 'POST':
            try:
                data[KEY_COMMENT] = "Created by administrator."
                # User is created by administrator, should be validated automatically, and credentials
                # should be sent to user by email.
                email_msg = """A TVB account was just created for you by an administrator.
                Your credentials are username=%s, password=%s.""" % (data[KEY_USERNAME], data[KEY_PASSWORD])
                self._create_user(email_msg=email_msg, validated=True, **data)
                basecontroller.set_info_message("New user created successfully.")
                redirect = True
            except formencode.Invalid, excep:
                template_specification[basecontroller.KEY_ERRORS] = excep.unpack_errors()
            except Exception, excep:
                self.logger.exceptrion(excep)
                basecontroller.set_error_message("We are very sorry, but we could not create your " +
                                                 "user. Most probably is because it was impossible" +
                                                 " to sent emails. Please try again later...")
        if redirect:
            raise cherrypy.HTTPRedirect('/user/usermanagement')
        else:
            return self.fill_default_attributes(template_specification)


    @cherrypy.expose
    @using_template('user/base_user')
    @admin()
    def usermanagement(self, cancel=False, page=1, do_persist=False, **data):
        """
        Display a table used for user management.
        """
        if cancel:
            raise cherrypy.HTTPRedirect('/user/profile')

        page = int(page)
        if cherrypy.request.method == 'POST' and do_persist:
            not_deleted = 0
            for key in data:
                user_id = int(key.split('_')[1])
                if 'delete_' in key:
                    self.user_service.delete_user(user_id)
                if ("role_" in key) and not (("delete_" + str(user_id)) in data):
                    valid = ("validate_" + str(user_id)) in data
                    user = self.user_service.get_user_by_id(user_id)
                    user.role = data[key]
                    user.validated = valid
                    self.user_service.edit_user(user)
                    not_deleted += 1
            # The entire current page was deleted, go to previous page
            if not_deleted == 0 and page > 1:
                page -= 1

        admin_ = basecontroller.get_logged_user().username
        user_list, pages_no = self.user_service.retrieve_all_users(admin_, page)
        template_specification = dict(mainContent="user_management", title="Users management", page_number=page,
                                      total_pages=pages_no, userList=user_list, allRoles=UserService.USER_ROLES,
                                      data={})
        return self.fill_default_attributes(template_specification)


    @cherrypy.expose
    @using_template('user/base_user')
    def recoverpassword(self, cancel=False, **data):
        """
        This form should reset a password for a given userName/email and send a 
        notification message to that email.
        """
        template_specification = dict(mainContent="recover_password", title="Recover password", data=data)
        redirect = False
        if cherrypy.request.method == 'POST':
            if cancel:
                raise cherrypy.HTTPRedirect('/user')
            form = RecoveryForm()
            try:
                data = form.to_python(data)
                okmessage = self.user_service.reset_password(**data)
                basecontroller.set_info_message(okmessage)
                redirect = True
            except formencode.Invalid, excep:
                template_specification[basecontroller.KEY_ERRORS] = excep.unpack_errors()
                redirect = False
            except UsernameException, excep1:
                self.logger.error("Could not reset password!")
                self.logger.exception(excep1)
                basecontroller.set_error_message(excep1.message)
                redirect = False
        if redirect:
            #Redirect to login page, with some success message to display
            raise cherrypy.HTTPRedirect('/user')
        else:
            #Stay on the same page
            return self.fill_default_attributes(template_specification)


    @cherrypy.expose
    @ajax_call()
    def upgrade_file_storage(self):
        """
        Upgrade the file storage to the latest version if needed.
        Otherwise just return. This is called on user login.
        """
        status, message = self.user_service.upgrade_file_storage()
        return dict(message=message, status=status)


    @cherrypy.expose
    @ajax_call()
    @admin()
    def validate(self, name):
        """
        A link to this page will be sent to the administrator to validate 
        the registration of each user.
        """
        success = self.user_service.validate_user(name)
        if not success:
            basecontroller.set_error_message("Problem validating user:" + name + "!! Please check logs.")
            self.logger.error("Problem validating user " + name)
        else:
            basecontroller.set_info_message("User Validated successfully and notification email sent!")
        raise cherrypy.HTTPRedirect('/tvb')


    def _create_user(self, email_msg=None, validated=False, **data):
        """
        Just create a user given the data input. Do form validation beforehand.
        """
        form = RegisterForm()
        data = form.to_python(data)
        data[KEY_PASSWORD] = md5(data[KEY_PASSWORD]).hexdigest()
        data['password2'] = md5(data['password2']).hexdigest()
        return self.user_service.create_user(email_msg=email_msg, validated=validated, **data)


    def fill_default_attributes(self, template_dictionary):
        """
        Fill into 'template_dictionary' data that we want to have ready in UI.
        """
        template_dictionary = self._populate_version(template_dictionary)
        basecontroller.BaseController.fill_default_attributes(self, template_dictionary)
        template_dictionary[basecontroller.KEY_INCLUDE_TOOLTIP] = True
        template_dictionary[basecontroller.KEY_WRAP_CONTENT_IN_MAIN_DIV] = False
        template_dictionary[basecontroller.KEY_CURRENT_TAB] = 'nav-user'
        return template_dictionary


    def _populate_version(self, template_dictionary):
        """
        Fill in template information about current version available online.
        """
        content = ""
        if self.version_info is None:
            try:
                content = urlopen(cfg.URL_TVB_VERSION, timeout=7).read()
                self.version_info = self.flow_service.parse_version_xml(str(content))
                pos = cfg.URL_TVB_VERSION.rfind('/')
                self.version_info['url'] = cfg.URL_TVB_VERSION[:pos]
            except Exception, excep:
                self.logger.warning("Could not read current version.xml!")
                self.logger.warning(content)
                self.logger.exception(excep)
                self.version_info = {}
        template_dictionary[KEY_SERVER_VERSION] = self.version_info
        template_dictionary[KEY_CURRENT_VERSION_FULL] = cfg.CURRENT_VERSION
        return template_dictionary



class LoginForm(formencode.Schema):
    """
    Validate for Login UI Form
    """
    empty_msg = 'Please enter a value'
    username = validators.UnicodeString(not_empty=True, use_builtins_gettext=False, messages={'empty': empty_msg})
    password = validators.UnicodeString(not_empty=True, use_builtins_gettext=False, messages={'empty': empty_msg})



class UniqueUsername(formencode.FancyValidator):
    """
    Custom validator to check that a given user-name is unique.
    """

    def _to_python(self, value, state):
        """ Fancy validate for Unique user-name """
        if not UserService().is_username_valid(value):
            raise formencode.Invalid('Please choose another user-name, this one is already in use!', value, state)
        return value



class RegisterForm(formencode.Schema):
    """
    Validate Register Form
    """
    username = formencode.All(validators.UnicodeString(not_empty=True), validators.PlainText(), UniqueUsername())
    password = validators.UnicodeString(not_empty=True)
    password2 = validators.UnicodeString(not_empty=True)
    email = validators.Email(not_empty=True)
    comment = validators.UnicodeString()
    role = validators.UnicodeString()
    chained_validators = [validators.FieldsMatch('password', 'password2')]



class RecoveryForm(formencode.Schema):
    """
    Validate Recover Password Form
    """
    username = formencode.All(validators.UnicodeString(not_empty=True), validators.PlainText())
    email = validators.Email(not_empty=True)



class EditUserForm(formencode.Schema):
    """   
    Validate fields on user-edit
    """
    old_password = validators.UnicodeString(if_missing=None)
    password = validators.UnicodeString(if_missing=None)
    password2 = validators.UnicodeString(if_missing=None)
    email = validators.Email(if_missing=None)
    chained_validators = [validators.FieldsMatch('password', 'password2'),
                          validators.RequireIfPresent('password', present='old_password')]
    
    
