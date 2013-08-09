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
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>

"""
import os
import unittest
import demoData.tables as dataset
from tvb.datatypes.lookup_tables import NerfTable, PsiTable
from tvb.core.entities.storage import dao
from tvb.core.adapters.abcadapter import ABCAdapter
from tvb.core.services.flowservice import FlowService
from tvb.core.entities.transient.structure_entities import DataTypeMetaData
from tvb_test.core.test_factory import TestFactory
from tvb_test.core.base_testcase import TransactionalTestCase


class LookupTableImporterTest(TransactionalTestCase):
    """
    Unit-tests for CFF-importer.
    """
    
    def setUp(self):
        """
        Reset the database before each test.
        """
        self.test_user = TestFactory.create_user('CFF_User')
        self.test_project = TestFactory.create_project(self.test_user, "CFF_Project")
        
    
    def test_psi_table_import(self):
        """
        Test that importing a CFF generates at least one DataType in DB.
        """
        dt_count_before = TestFactory.get_entity_count(self.test_project, PsiTable())
        group = dao.find_group('tvb.adapters.uploaders.lookup_table_importer', 'LookupTableImporter')
        importer = ABCAdapter.build_adapter(group)
        importer.meta_data = {DataTypeMetaData.KEY_SUBJECT: DataTypeMetaData.DEFAULT_SUBJECT,
                              DataTypeMetaData.KEY_STATE: "RAW"}
        zip_path = os.path.join(os.path.abspath(os.path.dirname(dataset.__file__)), 'psi.npz')
        args = {'psi_table_file': zip_path, 'table_type' : 'Psi Table'}
        ### Launch Operation
        FlowService().fire_operation(importer, self.test_user, self.test_project.id, **args)
        dt_count_after = TestFactory.get_entity_count(self.test_project, PsiTable())
        self.assertTrue(dt_count_after == dt_count_before + 1)
        
        
    def test_nerf_table_import(self):
        """
        Test that importing a CFF generates at least one DataType in DB.
        """
        dt_count_before = TestFactory.get_entity_count(self.test_project, NerfTable())
        group = dao.find_group('tvb.adapters.uploaders.lookup_table_importer', 'LookupTableImporter')
        importer = ABCAdapter.build_adapter(group)
        importer.meta_data = {DataTypeMetaData.KEY_SUBJECT: DataTypeMetaData.DEFAULT_SUBJECT,
                              DataTypeMetaData.KEY_STATE: "RAW"}
        zip_path = os.path.join(os.path.abspath(os.path.dirname(dataset.__file__)), 'nerf_int.npz')
        args = {'psi_table_file': zip_path, 'table_type' : 'Nerf Table'}
        ### Launch Operation
        FlowService().fire_operation(importer, self.test_user, self.test_project.id, **args)
        dt_count_after = TestFactory.get_entity_count(self.test_project, NerfTable())
        self.assertTrue(dt_count_after == dt_count_before + 1)
    
        
def suite():
    """
    Gather all the tests in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(LookupTableImporterTest))
    return test_suite


if __name__ == "__main__":
    #So you can run tests from this package individually.
    TEST_RUNNER = unittest.TextTestRunner()
    TEST_SUITE = suite()
    TEST_RUNNER.run(TEST_SUITE)
    
    
    
       
        
        
        
    