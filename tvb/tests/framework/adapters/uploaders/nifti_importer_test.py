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
.. moduleauthor:: Calin Pavel <calin.pavel@codemart.ro>
"""

import os
import numpy
import tvb_data.nifti as demo_data
from cherrypy._cpreqbody import Part
from cherrypy.lib.httputil import HeaderMap

from tvb.adapters.uploaders.nifti_importer import NIFTIImporterForm
from tvb.core.entities.model.datatypes.connectivity import ConnectivityIndex

from tvb.tests.framework.core.base_testcase import TransactionalTestCase
from tvb.tests.framework.core.factory import TestFactory
from tvb.core.entities.file.files_helper import FilesHelper
from tvb.core.entities.storage import dao
from tvb.core.entities.transient.structure_entities import DataTypeMetaData
from tvb.core.services.flow_service import FlowService
from tvb.core.services.exceptions import OperationException
from tvb.core.adapters.abcadapter import ABCAdapter
from tvb.datatypes.region_mapping import RegionVolumeMapping
from tvb.datatypes.time_series import TimeSeriesVolume
from tvb.datatypes.structural import StructuralMRI


class TestNIFTIImporter(TransactionalTestCase):
    """
    Unit-tests for NIFTI importer.
    """

    NII_FILE = os.path.join(os.path.dirname(demo_data.__file__), 'minimal.nii')
    GZ_NII_FILE = os.path.join(os.path.dirname(demo_data.__file__), 'minimal.nii.gz')
    TIMESERIES_NII_FILE = os.path.join(os.path.dirname(demo_data.__file__), 'time_series_152.nii.gz')
    WRONG_NII_FILE = os.path.abspath(__file__)
    TXT_FILE = os.path.join(os.path.dirname(demo_data.__file__), 'text_file.txt')

    DEFAULT_ORIGIN = [[0.0, 0.0, 0.0]]
    UNKNOWN_STR = "unknown"

    def _import(self, test_user, test_project, import_file_path=None, expected_result_class=StructuralMRI, connectivity=None):
        """
        This method is used for importing data in NIFIT format
        :param import_file_path: absolute path of the file to be imported
        """

        ### Retrieve Adapter instance 
        importer = TestFactory.create_adapter('tvb.adapters.uploaders.nifti_importer', 'NIFTIImporter')

        form = NIFTIImporterForm()
        form.fill_from_post({'_data_file': Part(import_file_path, HeaderMap({}), ''),
                             '_apply_corrections': 'True',
                             '_connectivity': connectivity,
                             '_mappings_file': Part(self.TXT_FILE, HeaderMap({}), ''),
                             '_Data_Subject': 'bla bla'
                             })
        form.data_file.data = import_file_path
        form.mappings_file.data = self.TXT_FILE
        importer.set_form(form)
        ### Launch import Operation
        FlowService().fire_operation(importer, test_user, test_project.id, **form.get_form_values())

        dts, count = dao.get_values_of_datatype(test_project.id, expected_result_class, None)
        assert 1, count == "Project should contain only one data type."

        result = ABCAdapter.load_entity_by_gid(dts[0][2])
        assert result is not None, "Result should not be none"
        return result

    def test_import_demo_ts(self, datatype_factory):
        """
        This method tests import of a NIFTI file.
        """
        time_series = self._import(datatype_factory['user'], datatype_factory['project'], self.TIMESERIES_NII_FILE, TimeSeriesVolume)

        # Since self.assertAlmostEquals is not available on all machine
        # We compare floats as following
        assert abs(1.0 - time_series.sample_period) <= 0.001
        assert "sec" == str(time_series.sample_period_unit)
        assert 0.0 == time_series.start_time
        assert time_series.title.startswith("NIFTI")

        data_shape = time_series.read_data_shape()
        assert 4 == len(data_shape)
        # We have 5 time points
        assert 5 == data_shape[0]
        dimension_labels = time_series.labels_ordering
        assert dimension_labels is not None
        assert 4 == len(dimension_labels)

        volume = time_series.volume
        assert volume is not None
        assert numpy.equal(self.DEFAULT_ORIGIN, volume.origin).all()
        assert "mm" == volume.voxel_unit

    def test_import_nii_without_time_dimension(self, datatype_factory):
        """
        This method tests import of a NIFTI file.
        """
        structure = self._import(datatype_factory['user'], datatype_factory['project'], self.NII_FILE)
        assert "T1" == structure.weighting

        data_shape = structure.array_data.shape
        assert 3 == len(data_shape)
        assert 64 == data_shape[0]
        assert 64 == data_shape[1]
        assert 10 == data_shape[2]

        volume = structure.volume
        assert volume is not None
        assert numpy.equal(self.DEFAULT_ORIGIN, volume.origin).all()
        assert numpy.equal([3.0, 3.0, 3.0], volume.voxel_size).all()
        assert self.UNKNOWN_STR == volume.voxel_unit

    def test_import_nifti_compressed(self, datatype_factory):
        """
        This method tests import of a NIFTI file compressed in GZ format.
        """
        structure = self._import(datatype_factory['user'], datatype_factory['project'], self.GZ_NII_FILE)
        assert "T1" == structure.weighting

    def test_import_region_mapping(self, connectivity_factory, datatype_factory):
        """
        This method tests import of a NIFTI file compressed in GZ format.
        """
        to_link_conn = connectivity_factory[1]
        cidx = ConnectivityIndex()
        cidx.fill_from_has_traits(to_link_conn)
        mapping = self._import(datatype_factory['user'], datatype_factory['project'], self.GZ_NII_FILE, RegionVolumeMapping, cidx)

        assert -1 <= mapping.array_data.min()
        assert mapping.array_data.max() < to_link_conn.number_of_regions

        conn = mapping.connectivity
        assert conn is not None
        assert to_link_conn.number_of_regions == conn.number_of_regions

        volume = mapping.volume
        assert volume is not None
        assert numpy.equal(self.DEFAULT_ORIGIN, volume.origin).all()
        assert numpy.equal([3.0, 3.0, 3.0], volume.voxel_size).all()
        assert self.UNKNOWN_STR == volume.voxel_unit

    def test_import_wrong_nii_file(self, datatype_factory):

        """ 
        This method tests import of a file in a wrong format
        """
        try:
            self._import(datatype_factory['user'], datatype_factory['project'], self.WRONG_NII_FILE)
            raise AssertionError("Import should fail in case of a wrong NIFTI format.")
        except OperationException:
            # Expected exception
            pass
