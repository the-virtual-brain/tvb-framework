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
Entry point for all tests.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""

import os
from sys import argv
from coverage import coverage

from tvb.basic.profile import TvbProfile as tvb_profile
#set the current environment to the test setup
tvb_profile.set_profile(argv)
from tvb.basic.config.settings import TVBSettings as cfg

KEY_CONSOLE = 'console'
KEY_COVERAGE = 'coverage'
KEY_XML = 'xml'



def generage_excludes(root_folders):
    """
    Specify excludes for Coverage.
    """
    excludes = []
    for root in root_folders:
        for root, _, files in os.walk(root):
            for file_n in files:
                full_path = os.path.join(root, file_n)
                if (full_path.endswith('__init__.py') or
                    os.path.join('interfaces', 'web', 'mplh5') in full_path or
                    os.path.join('interfaces', 'web', 'static') in full_path or
                    os.path.join('interfaces', 'web', 'templates') in full_path or
                    os.path.join('entities', 'model', 'db_update_scripts') in full_path or
                        os.path.join('tvb', 'simulator') in full_path or 'scientific_library' in full_path):
                    excludes.append(full_path)
    return excludes



if __name__ == "__main__":
    #Start all TVB tests (if in Coverage mode)
    if KEY_COVERAGE in argv:
        import tvb.interfaces as intf

        SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(intf.__file__)))
        COVERAGE = coverage(source=[SOURCE_DIR], omit=generage_excludes([SOURCE_DIR]), cover_pylib=False)
        COVERAGE.start()
        ## This needs to be executed before any TVB import.

import unittest
import datetime

# Make sure folder for Logging exists.   
if not os.path.exists(cfg.TVB_STORAGE):
    os.makedirs(cfg.TVB_STORAGE)

import matplotlib
matplotlib.use('module://tvb.interfaces.web.mplh5.mplh5_backend')
from tvb_test.xmlrunner import XMLTestRunner
from tvb_test.core import core_tests_main
from tvb_test.adapters import adapters_tests_main
from tvb_test.analyzers import bct_test
from tvb_test.interfaces.web import web_tests_main



def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(core_tests_main.suite())
    test_suite.addTest(adapters_tests_main.suite())
    test_suite.addTest(bct_test.suite())
    test_suite.addTest(web_tests_main.suite())
    return test_suite



if __name__ == "__main__":
    #Start all TVB tests
    START_TIME = datetime.datetime.now()

    if KEY_CONSOLE in argv:
        TEST_RUNNER = unittest.TextTestRunner()
        TEST_SUITE = suite()
        TEST_RUNNER.run(TEST_SUITE)
    if KEY_XML in argv:
        FILE_NAME = "TEST-RESULTS.xml"
        STREAM = file(FILE_NAME, "w")
        TEST_RUNNER = XMLTestRunner(STREAM)
        TEST_SUITE = suite()
        TEST_RUNNER.run(TEST_SUITE)
        STREAM.close()

    print 'It run tests for %d sec.' % (datetime.datetime.now() - START_TIME).seconds

    if KEY_COVERAGE in argv:
        COVERAGE.stop()
        COVERAGE.html_report(directory=os.path.join(os.path.dirname(__file__), 'test_coverage_html'))

