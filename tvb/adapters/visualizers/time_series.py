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
A Javascript displayer for time series, using SVG.

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import os
import json
from abc import ABCMeta
from six import add_metaclass
from tvb.core.entities.file.datatypes.connectivity_h5 import ConnectivityH5
from tvb.core.entities.file.datatypes.sensors_h5 import SensorsH5
from tvb.core.entities.file.datatypes.time_series_h5 import TimeSeriesRegionH5, TimeSeriesSensorsH5
from tvb.core.entities.filters.chain import FilterChain
from tvb.core.adapters.abcadapter import ABCAdapterForm
from tvb.core.adapters.abcdisplayer import ABCDisplayer, URLGenerator
from tvb.core.entities.model.datatypes.time_series import TimeSeriesIndex
from tvb.core.neotraits._forms import DataTypeSelectField
from tvb.core.neocom.h5 import DirLoader
from tvb.core.neocom.config import registry


class TimeSeriesForm(ABCAdapterForm):

    def __init__(self, prefix='', project_id=None):
        super(TimeSeriesForm, self).__init__(prefix, project_id, False)

        self.time_series = DataTypeSelectField(self.get_required_datatype(), self, name='time_series', required=True,
                                               label="Time series to be displayed in a 2D form.",
                                               conditions=self.get_filters())

    @staticmethod
    def get_required_datatype():
        return TimeSeriesIndex

    @staticmethod
    def get_input_name():
        return '_time_series'

    @staticmethod
    def get_filters():
        return FilterChain(fields=[FilterChain.datatype + '.time_series_type'],
                           operations=["!="],
                           values=["TimeSeriesVolume"])


@add_metaclass(ABCMeta)
class ABCSpaceDisplayer(ABCDisplayer):

    def build_template_params_for_subselectable_datatype(self, sub_selectable):
        """
        creates a template dict with the initial selection to be
        displayed in a time series viewer
        """
        return {'measurePointsSelectionGID': sub_selectable.gid.load().hex,
                'initialSelection': self.get_default_selection(sub_selectable),
                'groupedLabels': self.get_grouped_space_labels(sub_selectable)}

    def get_space_labels(self, ts_h5):
        """
        :return: An array of strings with the connectivity node labels.
        """

        if type(ts_h5) is TimeSeriesRegionH5:
            connectivity_gid = ts_h5.connectivity.load()
            if connectivity_gid is None:
                return []

            connectivity_h5_class, connectivity_h5_path = self._load_h5_of_gid(connectivity_gid.hex)
            connectivity_h5 = connectivity_h5_class(connectivity_h5_path)
            return list(connectivity_h5.region_labels.load())

        if type(ts_h5) is TimeSeriesSensorsH5:
            sensors_gid = ts_h5.sensors.load()
            if sensors_gid is None:
                return []

            sensors_h5_class, sensors_h5_path = self._load_h5_of_gid(sensors_gid.hex)
            sensors_h5 = sensors_h5_class(sensors_h5_path)
            return list(sensors_h5.labels.load())

        return ts_h5.get_space_labels

    def get_grouped_space_labels(self, h5_file):
        """
        :return: A structure of this form [('left', [(idx, lh_label)...]), ('right': [(idx, rh_label) ...])]
        """

        if type(h5_file) is ConnectivityH5:
            return h5_file.get_grouped_space_labels()

        connectivity_gid = h5_file.connectivity.load()
        if connectivity_gid is None:
            return super(type(h5_file), h5_file).get_grouped_space_labels()

        connectivity_h5_class, connectivity_h5_path = self._load_h5_of_gid(connectivity_gid.hex)
        connectivity_h5 = connectivity_h5_class(connectivity_h5_path)
        return connectivity_h5.get_grouped_space_labels()

    def get_default_selection(self, h5_file):
        """
        :return: If the connectivity of this time series is edited from another
                 return the nodes of the parent that are present in the connectivity.
        """
        if type(h5_file) in [ConnectivityH5, SensorsH5]:
            return h5_file.get_default_selection()

        connectivity_gid = h5_file.connectivity.load()
        if connectivity_gid is None:
            return super(type(h5_file), h5_file).get_default_selection()

        connectivity_h5_class, connectivity_h5_path = self._load_h5_of_gid(connectivity_gid.hex)
        connectivity_h5 = connectivity_h5_class(connectivity_h5_path)
        return connectivity_h5.get_default_selection()


class TimeSeries(ABCSpaceDisplayer):
    _ui_name = "Time Series Visualizer (SVG/d3)"
    _ui_subsection = "timeseries"

    MAX_PREVIEW_DATA_LENGTH = 200

    def get_form_class(self):
        return TimeSeriesForm

    def get_required_memory_size(self, **kwargs):
        """Return required memory."""
        return -1

    def launch(self, time_series, preview=False, figsize=None):
        """Construct data for visualization and launch it."""
        dir_loader = DirLoader(os.path.join(os.path.dirname(self.storage_path), str(time_series.fk_from_operation)))
        time_series_h5_class = registry.get_h5file_for_index(type(time_series))
        time_series_path = dir_loader.path_for(time_series_h5_class, time_series.gid)

        h5_file = time_series_h5_class(time_series_path)
        shape = list(h5_file.read_data_shape())
        ts = h5_file.storage_manager.get_data('time')
        state_variables = h5_file.labels_dimensions.load().get(time_series.labels_ordering[1], [])
        labels = self.get_space_labels(h5_file)

        # Assume that the first dimension is the time since that is the case so far
        if preview and shape[0] > self.MAX_PREVIEW_DATA_LENGTH:
            shape[0] = self.MAX_PREVIEW_DATA_LENGTH

        # when surface-result, the labels will be empty, so fill some of them,
        # but not all, otherwise the viewer will take ages to load.
        if shape[2] > 0 and len(labels) == 0:
            for n in range(min(self.MAX_PREVIEW_DATA_LENGTH, shape[2])):
                labels.append("Node-" + str(n))

        pars = {'baseURL': URLGenerator.build_base_h5_url(time_series.gid),
                'labels': labels, 'labels_json': json.dumps(labels),
                'ts_title': time_series.title, 'preview': preview, 'figsize': figsize,
                'shape': repr(shape), 't0': ts[0],
                'dt': ts[1] - ts[0] if len(ts) > 1 else 1,
                'labelsStateVar': state_variables, 'labelsModes': range(shape[3])
                }
        pars.update(self.build_template_params_for_subselectable_datatype(h5_file))
        h5_file.close()

        return self.build_display_result("time_series/view", pars, pages=dict(controlPage="time_series/control"))

    def generate_preview(self, time_series, figure_size):
        return self.launch(time_series, preview=True, figsize=figure_size)
