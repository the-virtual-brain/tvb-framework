# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and 
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
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
module docstring
.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
"""

import pytest
import os.path
import tvb_data
from cherrypy._cpreqbody import Part
from cherrypy.lib.httputil import HeaderMap
from tvb.adapters.uploaders.cff_importer import CFFImporterForm

from tvb.tests.framework.core.base_testcase import TransactionalTestCase
from tvb.core.entities.file.files_helper import FilesHelper
from tvb.core.services.exceptions import OperationException
from tvb.datatypes.connectivity import Connectivity
from tvb.datatypes.graph import ConnectivityMeasure
from tvb.tests.framework.core.factory import TestFactory
from tvb.core.services.flow_service import FlowService


class TestConnectivityMeasureImporter(TransactionalTestCase):
    """
    Unit-tests for ConnectivityMeasureImporter
    """

    def transactional_setup_method(self):
        zip_path = os.path.join(os.path.dirname(tvb_data.__file__), 'connectivity', 'connectivity_66.zip')
        self.test_user = TestFactory.create_user('Test_User')
        self.test_project = TestFactory.create_project(self.test_user, "Test_Project")
        TestFactory.import_zip_connectivity(self.test_user,self.test_project, "John", zip_path)
        self.connectivity = TestFactory.get_entity(self.test_project, Connectivity())


    def transactional_teardown_method(self):
        FilesHelper().remove_project_structure(self.test_project.name)


    def _import(self, import_file_name):
        ### Retrieve Adapter instance
        importer = TestFactory.create_adapter('tvb.adapters.uploaders.cff_importer', 'CFF_Importer')
        form = CFFImporterForm()
        form.fill_from_post({'_cff': Part(self.VALID_CFF, HeaderMap({}), ''), '_Data_Subject': 'John Doe',
                             '_key_edge_weight': 'adc_mean', '_key_edge_tract': 'fiber_length_mean',
                             '_key_node_coordinates': 'dn_position', '_key_node_label': 'dn_name',
                             '_key_node_region': 'dn_region', '_key_node_hemisphere': 'dn_hemisphere'
                             })
        form.cff.data = import_file_name
        importer.set_form(form)

        # Launch Operation
        FlowService().fire_operation(importer, self.test_user, self.test_project.id, **form.get_dict())


def test_happy_flow(self):
        assert 0 == TestFactory.get_entity_count(self.test_project, ConnectivityMeasure())
        self._import('mantini_networks.mat')
        assert 6 == TestFactory.get_entity_count(self.test_project, ConnectivityMeasure())

    def test_connectivity_mismatch(self):
        with pytest.raises(OperationException):
            self._import( 'mantini_networks_33.mat')

