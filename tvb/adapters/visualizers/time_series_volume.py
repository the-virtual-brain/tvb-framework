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
Backend-side for TS Visualizer of TS Volume DataTypes.

.. moduleauthor:: Robert Parcus <betoparcus@gmail.com>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Ciprian Tomoiaga <ciprian.tomoiaga@codemart.ro>

"""

import json
from tvb.basic.filters.chain import FilterChain
from tvb.adapters.visualizers.region_volume_mapping import _MappedArrayVolumeBase
from tvb.core.adapters.abcadapter import ABCAdapterForm
from tvb.core.adapters.abcdisplayer import ABCDisplayer
from tvb.core.entities.file.datatypes.time_series import TimeSeriesVolumeH5
from tvb.core.entities.model.datatypes.structural import StructuralMRIIndex
from tvb.core.entities.model.datatypes.time_series import TimeSeriesIndex
from tvb.core.entities.storage import dao

from tvb.core.neotraits._forms import DataTypeSelectField


class TimeSeriesVolumeVisualiserForm(ABCAdapterForm):

    def __init__(self, prefix='', project_id=None):
        super(TimeSeriesVolumeVisualiserForm, self).__init__(prefix, project_id)
        self.time_series = DataTypeSelectField(self.get_required_datatype(), self, name='time_series', required=True,
                                               label='Time Series', conditions=self.get_filters())
        self.background = DataTypeSelectField(StructuralMRIIndex, self, name='background', required=False,
                                              label='Background T1')

    @staticmethod
    def get_input_name():
        return '_time_series'

    @staticmethod
    def get_filters():
        return FilterChain(fields=[FilterChain.datatype + '.has_volume_mapping'], operations=["=="], values=[True])

    @staticmethod
    def get_required_datatype():
        return TimeSeriesIndex


class TimeSeriesVolumeVisualiser(ABCDisplayer):

    _ui_name = "Time Series Volume Visualizer"
    _ui_subsection = "volume"
    form = None

    def get_input_tree(self): return None

    def get_form(self):
        if self.form is None:
            return TimeSeriesVolumeVisualiserForm
        return self.form

    def set_form(self, form):
        self.form = form

    def get_required_memory_size(self, **kwargs):
        """Return required memory."""
        return -1


    def launch(self, time_series, background=None):

        url_volume_data = self.build_url('get_volume_view', time_series.gid, '')
        url_timeseries_data = self.build_url('get_voxel_time_series', time_series.gid, '')

        ts_h5_class, ts_h5_path = self._load_h5_of_gid(time_series.gid)
        ts_h5 = ts_h5_class(ts_h5_path)
        min_value, max_value = ts_h5.get_min_max_values()

        if isinstance(ts_h5, TimeSeriesVolumeH5):
            volume_h5_class, volume_h5_path = self._load_h5_of_gid(ts_h5.volume.load().hex)
            volume_h5 = volume_h5_class(volume_h5_path)
            volume_shape = ts_h5.data.shape
        else:
            rmv_index = self.load_entity_by_gid(ts_h5.region_mapping_volume.load(True).hex)
            rmv_h5_class, rmv_h5_path = self._load_h5_of_gid(rmv_index.gid)
            rmv_h5 = rmv_h5_class(rmv_h5_path)
            volume_index = self.load_entity_by_gid(rmv_h5.volume.load().hex)
            volume_h5_class, volume_h5_path = self._load_h5_of_gid(volume_index.gid)
            volume_h5 = volume_h5_class(volume_h5_path)
            volume_shape = [ts_h5.data.shape[0]]
            volume_shape.extend(rmv_h5.array_data.shape)
            rmv_h5.close()

        params = dict(title="Volumetric Time Series",
                      ts_title=ts_h5.title.load(),
                      labelsStateVar=ts_h5.labels_dimensions.load().get(ts_h5.labels_ordering.load()[1], []),
                      labelsModes=range(ts_h5.data.shape[3]),
                      minValue=min_value, maxValue=max_value,
                      urlVolumeData=url_volume_data,
                      urlTimeSeriesData=url_timeseries_data,
                      samplePeriod=ts_h5.sample_period.load(),
                      samplePeriodUnit=ts_h5.sample_period_unit.load(),
                      volumeShape=json.dumps(volume_shape),
                      volumeOrigin=json.dumps(volume_h5.origin.load().tolist()),
                      voxelUnit=volume_h5.voxel_unit.load(),
                      voxelSize=json.dumps(volume_h5.voxel_size.load().tolist()))

        params.update(self.ensure_background(background))

        volume_h5.close()
        ts_h5.close()
        return self.build_display_result("time_series_volume/view", params,
                                         pages=dict(controlPage="time_series_volume/controls"))

    def ensure_background(self, background_index):
        if background_index is None:
            background_index = dao.try_load_last_entity_of_type(self.current_project_id, StructuralMRIIndex)

        if background_index is None:
            return _MappedArrayVolumeBase.compute_background_params()

        background_class, background_path = self._load_h5_of_gid(background_index.gid)
        background_h5 = background_class(background_path)
        min_value, max_value = background_h5.get_min_max_values()
        background_h5.close()

        url_volume_data = self.build_url('get_volume_view', background_index.gid, '')
        return _MappedArrayVolumeBase.compute_background_params(min_value, max_value, url_volume_data)