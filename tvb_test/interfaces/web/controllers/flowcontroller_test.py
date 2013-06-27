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
.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""
import unittest
import cherrypy
import tvb.interfaces.web.controllers.basecontroller as b_c
from tvb.interfaces.web.controllers.flowcontroller import FlowController
from tvb.core.entities.storage import dao
from tvb_test.adapters.testadapter1 import TestAdapter1
from tvb_test.datatypes.datatypes_factory import DatatypesFactory
from tvb_test.core.base_testcase import TransactionalTestCase
from tvb_test.interfaces.web.controllers.basecontroller_test import BaseControllersTest


class FlowContollerTest(TransactionalTestCase, BaseControllersTest):
    """ Unit tests for flowcontoller """
    
    def setUp(self):
        """
        Sets up the environment for testing;
        creates a `FlowController`
        """
        BaseControllersTest.init(self)
        self.flow_c =  FlowController()
    
    
    def tearDown(self):
        """ Cleans up the testing environment """
        BaseControllersTest.cleanup(self)
            
            
    def test_context_selected(self):
        """
        Remove the project from cherrypy session and check that you are
        redirected to projects page.
        """
        del cherrypy.session[b_c.KEY_PROJECT]
        self._expect_redirect('/project/viewall', self.flow_c.step)
    

    def test_invalid_step(self):
        """
        Pass an invalid step and make sure we are redirected to tvb start page.
        """
        self._expect_redirect('/tvb', self.flow_c.step)
        
        
    def test_valid_step(self):
        """
        For all algorithm categories check that a submenu is generated and the result
        page has it's title given by category name.
        """
        categories = dao.get_algorithm_categories()
        for categ in categories:
            result_dict = self.flow_c.step(categ.id)
            self.assertTrue(b_c.KEY_SUBMENU_LIST in result_dict, 
                            "Expect to have a submenu with available algorithms for category.")
            self.assertEqual(result_dict["section_name"], categ.displayname.lower())


    def test_step_connectivity(self):
        """
        Check that the correct section name and connectivity submenu are returned for the 
        connectivity step.
        """
        result_dict = self.flow_c.step_connectivity()
        self.assertEqual(result_dict['section_name'], 'connectivity')
        self.assertEqual(result_dict['submenu_list'], self.flow_c.connectivity_submenu)


    def test_default(self):
        """
        Test default method from step controllers. Check that the submit link is ok, that a mainContent
        is present in result dict and that the isAdapter flag is set to true.
        """
        cherrypy.request.method = "GET"
        categories = dao.get_algorithm_categories()
        for categ in categories:
            algo_groups = dao.get_groups_by_categories([categ.id])
            for algo in algo_groups:
                result_dict = self.flow_c.default(categ.id, algo.id)
                self.assertEqual(result_dict[b_c.KEY_SUBMIT_LINK], '/flow/%i/%i'%(categ.id, algo.id))
                self.assertTrue('mainContent' in result_dict)
                self.assertTrue(result_dict['isAdapter'])
                
                
    def test_default_cancel(self):
        """
        On cancel we should get a redirect to the back page link.
        """
        cherrypy.request.method = "POST"
        categories = dao.get_algorithm_categories()
        algo_groups = dao.get_groups_by_categories([categories[0].id])
        self._expect_redirect('/project/viewoperations/%i'%(self.test_project.id), 
                              self.flow_c.default, categories[0].id, algo_groups[0].id, 
                              cancel=True, back_page='operations')
        
        
    def test_default_invalid_key(self):
        """
        Pass invalid keys for adapter and step and check you get redirect to tvb entry
        page with error set.
        """
        self._expect_redirect('/tvb?error=True', self.flow_c.default, 'invalid', 'invalid')
        
        
    def test_read_datatype_attribute(self):
        """
        Read an attribute from a datatype.
        """
        dt = DatatypesFactory().create_datatype_with_storage("test_subject", "RAW_STATE", 'this is the stored data'.split())
        returned_data = self.flow_c.read_datatype_attribute(dt.gid, "string_data")
        self.assertEqual(returned_data, '["this", "is", "the", "stored", "data"]')
        
        
    def test_read_datatype_attribute_method_call(self):
        """
        Call method on given datatype.
        """
        dt = DatatypesFactory().create_datatype_with_storage("test_subject", "RAW_STATE", 'this is the stored data'.split())
        args = {'length' : 101}
        returned_data = self.flow_c.read_datatype_attribute(dt.gid, 'return_test_data', **args)
        self.assertTrue(returned_data == str(range(101)))
        
        
    def test_get_simple_adapter_interface(self):
        adapter = dao.find_group('tvb_test.adapters.testadapter1', 'TestAdapter1')
        result = self.flow_c.get_simple_adapter_interface(adapter.id)
        expected_interface = TestAdapter1().get_input_tree()
        self.assertEqual(result['inputList'], expected_interface)

def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(FlowContollerTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE)
