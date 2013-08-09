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
""""
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""
import os
import unittest
from tvb.core.services.dtipipelineservice import DTIPipelineService
from tvb.core.entities.file.fileshelper import FilesHelper
from tvb.basic.traits.util import read_list_data
from tvb_test.core.test_factory import TestFactory
from tvb_test.core.base_testcase import TransactionalTestCase
import tvb_test.core.services as current_pack


class DTITest(TransactionalTestCase):
    """
    Test basic functionality of DTI Import Service.
    """
    ### First dataSet
    FILE_1 = os.path.join(os.path.dirname(current_pack.__file__), "data", "TVB_ConnectionCapacityMatrix.csv")
    FILE_2 = os.path.join(os.path.dirname(current_pack.__file__), "data", "TVB_ConnectionDistanceMatrix.csv")
    ### Second dataSet
    FILE_3 = os.path.join(os.path.dirname(current_pack.__file__), "data", "TVB_ConnectionCapacityMatrix_3.csv")
    FILE_4 = os.path.join(os.path.dirname(current_pack.__file__), "data", "TVB_ConnectionDistanceMatrix_3.csv")
    
    
    def setUp(self):
        """
        Reset the database before each test.
        """
#        self.clean_database()
        self.test_user = TestFactory.create_user()
        self.test_project = TestFactory.create_project(self.test_user)
        self.service = DTIPipelineService('127.0.0.1', 'root')
        self.helper = FilesHelper()
      
      
    def test_process_csv(self):
        """
        Test that a CSV generated on the server is correctly processed.
        """
        
        folder = self.helper.get_project_folder(self.test_project, "TEMP")
        
        for file_name in [self.FILE_1, self.FILE_2, self.FILE_3, self.FILE_4]:
            
            intermediate_file = os.path.join(folder, os.path.split(file_name)[1])
            self.helper.copy_file(file_name, intermediate_file)
            result_file = 'weights.txt' if 'Capacity' in file_name else 'tracts.txt'
            result_file = os.path.join(folder, result_file)
            self.service._process_csv_file(intermediate_file, result_file)
            matrix = read_list_data(result_file)
            self.assertEqual(96, len(matrix))
            self.assertEqual(96, len(matrix[0]))
        
        
#    def test_gather_results(self):
#        """
#        Test that after importing data from the server
#        """
#        folder = self.helper.get_project_folder(self.test_project, "TEMP")
#        self.helper.copy_file(self.FILE_1, os.path.join(folder, self.FILE_1))
#        self.helper.copy_file(self.FILE_2, os.path.join(folder, self.FILE_2))
#        self.service._gather_results(self.test_user, self.test_project, os.path.join(folder, self.FILE_1), 
#                                     os.path.join(folder, self.FILE_1), folder, "zip_output")
        
        
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(DTITest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run (TEST_SUITE)       
    
    
    
          
        