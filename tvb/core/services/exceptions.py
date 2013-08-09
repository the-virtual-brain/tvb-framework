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
Exceptions for services layer of the application. 
   
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""
from tvb.basic.traits.exceptions import TVBException



class ServicesBaseException(TVBException):
    """
    Base Exception class for Services layer in the application.
    """


    def __init__(self, message, parent_exception=None):
        TVBException.__init__(self, message, parent_exception)



class StructureException(ServicesBaseException):
    """
    Exception to be thrown in case of a problem related to Structure Storage.
    """


    def __init__(self, message):
        ServicesBaseException.__init__(self, message)



class OperationException(ServicesBaseException):
    """
    Exception to be thrown in case of a problem related to Launching 
    and Executing TVB specific Operations.
    """


    def __init__(self, message, parent_exception=None):
        ServicesBaseException.__init__(self, message, parent_exception)



class UsernameException(ServicesBaseException):
    """
    Exception to be thrown in case of a problem related to creating
    or managing a user.
    """


    def __init__(self, message):
        ServicesBaseException.__init__(self, message)



class WorkflowException(ServicesBaseException):
    """
    Exception to be thrown in case of a problem related to creating
    or managing a workflow.
    """


    def __init__(self, message):
        ServicesBaseException.__init__(self, message)



class WorkflowInterStepsException(WorkflowException):
    """
    Exception to be thrown in case of a problem happened between steps of a workflow.
    Status ERROR needs to be reported at a top level (e.g. Burst) as workflow 
    steps individually can not be made responsible.
    """


    def __init__(self, message):
        WorkflowException.__init__(self, message)



class ProjectServiceException(ServicesBaseException):
    """
    Exception to be thrown in case of a problem in the projectservice
    module.
    """


    def __init__(self, message):
        ServicesBaseException.__init__(self, message)



class ProjectImportException(ServicesBaseException):
    """
    Exception to be thrown in case of a problem at project import.
    """


    def __init__(self, message):
        ServicesBaseException.__init__(self, message)



class BurstServiceException(ServicesBaseException):
    """
    Exception to be thrown in case of a problem at project import.
    """


    def __init__(self, message):
        ServicesBaseException.__init__(self, message)



class InvalidPortletConfiguration(ServicesBaseException):
    """
    Exception thrown in cases related to wrong portlet configurations.
    """


    def __init__(self, message):
        ServicesBaseException.__init__(self, message)



class InvalidSettingsException(ServicesBaseException):
    """
    Exception to be thrown in case of a problem at project import.
    """


    def __init__(self, message):
        ServicesBaseException.__init__(self, message)



class RemoveDataTypeException(ServicesBaseException):
    """
    Exception to be thrown in case some one tries to remove an
    entity that is used by other entities.
    """


    def __init__(self, message):
        ServicesBaseException.__init__(self, message)



class RemoveDataTypeError(ServicesBaseException):
    """
    Exception to be thrown in case some one tries to remove an entity that should
    not be possible to be removed. E.g. If some one tries to remove the array
    wrapper corresponding to a time series (inheritance relationship).
    """


    def __init__(self, message):
        ServicesBaseException.__init__(self, message)



class ConnectException(ServicesBaseException):
    """ 
    Exception to be thrown when DTI Pipeline error happened.  
    """
    pass






        