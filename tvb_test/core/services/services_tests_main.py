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
from tvb_test.core.services import projectservice_test
from tvb_test.core.services import projectstructure_test
from tvb_test.core.services import burstservice_test
from tvb_test.core.services import userservice_test
from tvb_test.core.services import eventhandler_test
from tvb_test.core.services import flowservice_test
from tvb_test.core.services import settingsservice_test
from tvb_test.core.services import importservice_test
from tvb_test.core.services import workflowservice_test
from tvb_test.core.services import operationservice_test
from tvb_test.core.services import remove_test
from tvb_test.core.services import dtipipelineservice_test


def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(projectservice_test.suite())
    test_suite.addTest(projectstructure_test.suite())
    test_suite.addTest(eventhandler_test.suite())
    test_suite.addTest(userservice_test.suite())
    test_suite.addTest(flowservice_test.suite())
    test_suite.addTest(settingsservice_test.suite())
    test_suite.addTest(burstservice_test.suite())
    test_suite.addTest(importservice_test.suite())
    test_suite.addTest(workflowservice_test.suite())
    test_suite.addTest(operationservice_test.suite())
    test_suite.addTest(remove_test.suite())
    test_suite.addTest(dtipipelineservice_test.suite())
    return test_suite


if __name__ == "__main__":
    #So you can run tests individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run (TEST_SUITE)
    
    