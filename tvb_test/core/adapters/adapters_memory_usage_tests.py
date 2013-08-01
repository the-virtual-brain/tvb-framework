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
#   Frontiers in Neuroinformatics (in press)
#
#

"""
Created on Jul 6, 2012

.. moduleauthor:: bogdan.neacsa <bogdan.neacsa@codemart.ro>
"""
import json
import unittest
from tvb.core.entities import model
from tvb.core.entities.storage import dao
from tvb.core.adapters.abcadapter import ABCAdapter
from tvb.core.adapters.exceptions import MethodUnimplementedException, NoMemoryAvailableException
from tvb.core.services.operationservice import OperationService
from tvb.core.services.flowservice import FlowService
from tvb_test.core.base_testcase import TransactionalTestCase
from tvb_test.core.test_factory import TestFactory


class AdapterMemoryUsageTest(TransactionalTestCase):
    """
    Test class for the introspector module.
    """
    
    def setUp(self):
        """
        Reset the database before each test.
        """
        self.test_user = TestFactory.create_user()
        self.test_project = TestFactory.create_project(admin=self.test_user)
    
    
    def test_adapter_memory_not_implemented(self):
        """
        Test that a method not implemeted exception is raised in case the
        get_required_memory_size method is not implemented.
        """
        module = "tvb_test.adapters.testadapter3"
        class_name = "TestAdapterNoMemoryImplemented"
        algo_group = dao.find_group(module, class_name)
        adapter = FlowService().build_adapter_instance(algo_group)
        data = {"test" : 5}
        
        operation = model.Operation(self.test_user.id, self.test_project.id, algo_group.id, 
                                         json.dumps(data), json.dumps({}), status=model.STATUS_STARTED,
                                         method_name = ABCAdapter.LAUNCH_METHOD)
        operation = dao.store_entity(operation)
        self.assertRaises(MethodUnimplementedException, OperationService().initiate_prelaunch, operation, adapter, {})
        
        
    def test_adapter_huge_memory_requirement(self):
        """
        Test that an MemoryException is raised in case adapter cant launch due to lack of memory.
        """
        module = "tvb_test.adapters.testadapter3"
        class_name = "TestAdapterHugeMemoryRequired"
        algo_group = dao.find_group(module, class_name)
        adapter = FlowService().build_adapter_instance(algo_group)
        data = {"test" : 5}
        
        operation = model.Operation(self.test_user.id, self.test_project.id, algo_group.id, 
                                         json.dumps(data), json.dumps({}), status=model.STATUS_STARTED,
                                         method_name = ABCAdapter.LAUNCH_METHOD)
        operation = dao.store_entity(operation)
        self.assertRaises(NoMemoryAvailableException, OperationService().initiate_prelaunch, operation, adapter, {})
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(AdapterMemoryUsageTest))
    return test_suite

if __name__ == "__main__":
    #So you can run tests from this package individually.
    unittest.main()     
        