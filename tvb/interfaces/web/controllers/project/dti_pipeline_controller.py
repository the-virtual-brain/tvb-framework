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
External storages/tools connect actions are grouped here.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

import cherrypy
import formencode
from formencode import validators
from cgi import FieldStorage
from tvb.core.services.dti_pipeline_service import DTIPipelineService
from tvb.interfaces.web.controllers.base_controller import using_template, BaseController
from tvb.interfaces.web.controllers.users_controller import logged
from tvb.interfaces.web.controllers.flow_controller import context_selected
import tvb.interfaces.web.controllers.base_controller as basecontroller
try:
    from cherrypy._cpreqbody import Part
    # cover cases when the web interface is not available.
except Exception:
    Part = FieldStorage
    
    
 
DEFAULT_FIELD_VALUES = {'server_ip': "127.0.0.1",
                        'username': 'erin',
                        'password': 'epipeline',
                        'threads_number': 4,
                        'subject_name': 'John Doe',
                        'subject_sex': 'Any'}


class DTIPipelineController(BaseController):
    """
    This class takes care of the connect actions with externals storage tools.
    """  
    
    def __init__(self):
        BaseController.__init__(self)


    @cherrypy.expose
    @using_template('base_template')
    @logged()
    @context_selected()
    def start_dti_pipeline(self, cancel=False, start=False, **data):
        """
        Prepare DTI Pipeline run.
        """
        project_id = basecontroller.get_current_project().id
        
        if cherrypy.request.method == 'POST' and cancel:
            raise cherrypy.HTTPRedirect("/project/editstructure/" + str(project_id))
        
        template_specification = dict(title="Import Connectivity", data=data, section_name='project',
                                      subsection_name='pipeline', mainContent="pipeline/get_connectivity",
                                      includedResources='project/included_resources')
        if cherrypy.request.method == 'POST' and start:
            form = ImportForm()
            try:
                data = form.to_python(data)
                service = DTIPipelineService(data['server_ip'], data['username'])
                current_project = basecontroller.get_current_project()
                current_user = basecontroller.get_logged_user()
                service.fire_pipeline(data['dti_scans'], current_project, current_user, data['threads_number'])
                okmessage = "Import Started! You will see results after few hours on Data Structure Page!"
                basecontroller.set_info_message(okmessage)
                raise cherrypy.HTTPRedirect("/project/editstructure/" + str(project_id))
            
            except formencode.Invalid, excep:
                basecontroller.set_error_message("Some parameters are invalid!")
                template_specification[basecontroller.KEY_ERRORS] = excep.unpack_errors()
        else:
            #Fill default attributes
            data.update(DEFAULT_FIELD_VALUES)
            
        return self.fill_default_attributes(template_specification)
    
    
 
class FileUploadValidator(validators.FancyValidator):
    """
    Create our own file-upload validation, as validators.FileUploadKeeper() is not working.
    """
    
    def _to_python(self, value, _status):
        
        content = None
        if isinstance(value, FieldStorage) or isinstance(value, Part):
            # filename = value.filename
            content = value.file
        elif isinstance(value, (str, unicode)):
            content = value
        ### Ignore uploaded file-name, as we do not need it in current form.
        return content
         
  
  
class ImportForm(formencode.Schema):
    """
    Validate for Import Connectivity Form
    """
    server_ip = validators.IPAddress(not_empty=True)
    username = validators.UnicodeString(not_empty=True)  
    password = validators.UnicodeString()
    threads_number = validators.Number()
    
    dti_scans = FileUploadValidator()
    
    subject_name = validators.UnicodeString()
    subject_sex = validators.OneOf(['Any', 'Male', 'Female'])  
    subject_age = validators.Number()
    subject_race = validators.UnicodeString()
    subject_nationality = validators.UnicodeString()
    subject_education = validators.UnicodeString()
    subject_health = validators.UnicodeString()
    
    

