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
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""
import json
import unittest
import cherrypy
import tvb.core.entities.model as model
from tvb.interfaces.web.controllers.burst.explorationcontroller import ParameterExplorationController
from tvb_test.core.base_testcase import TransactionalTestCase
from tvb_test.interfaces.web.controllers.basecontroller_test import BaseControllersTest
from tvb_test.datatypes.datatypes_factory import DatatypesFactory



class ExplorationContollerTest(TransactionalTestCase, BaseControllersTest):
    """
    Unit tests for BurstController
    """


    def setUp(self):
        """
        Sets up the environment for testing;
        creates a datatype group and a Parameter Exploration Controller
        """
        BaseControllersTest.init(self)
        self.dt_group = DatatypesFactory().create_datatype_group()
        self.controller = ParameterExplorationController()


    def tearDown(self):
        """ Cleans the testing environment """
        BaseControllersTest.cleanup(self)


    def test_draw_discrete_exploration(self):
        """
        Test that Discrete PSE is getting launched.
        """
        result = self.controller.draw_discrete_exploration(self.dt_group.gid, 'burst', None, None)
        self.assertTrue(result['available_metrics'] == [])
        self.assertEqual(result['color_metric'], None)
        self.assertEqual(result['size_metric'], None)
        self.assertEqual(json.loads(result['labels_x']), ['a', 'b', 'c'])
        self.assertEqual(json.loads(result['labels_y']), [model.RANGE_MISSING_STRING])
        data = json.loads(result['data'])
        self.assertEqual(len(data), 3)
        for entry in data:
            self.assertEqual(entry[0]['dataType'], 'Datatype2')
            for key in ['Gid', 'color_weight', 'operationId', 'tooltip']:
                self.assertTrue(key in entry[0])


    def test_draw_isocline_exploration(self):
        """
        Test that isocline PSE does not get launched for 1D groups.
        """
        try:
            self.controller.draw_isocline_exploration(self.dt_group.gid, 50, 50)
            self.fail("It should have thrown an exception because ")
        except cherrypy.HTTPRedirect:
            pass



def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ExplorationContollerTest))
    return test_suite



if __name__ == "__main__":
    #So you can run tests individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE)