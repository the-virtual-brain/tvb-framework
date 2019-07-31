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


from tvb.adapters.visualizers.brain import BrainViewer
from tvb.adapters.visualizers.eeg_monitor import EegMonitor
from tvb.adapters.visualizers.sensors import prepare_sensors_as_measure_points_params
from tvb.adapters.visualizers.sensors import prepare_mapped_sensors_as_measure_points_params
from tvb.basic.filters.chain import FilterChain
from tvb.core.entities.storage import dao
from tvb.datatypes.surfaces import EEGCap, CorticalSurface
from tvb.datatypes.surfaces import Surface
from tvb.datatypes.time_series import TimeSeries, TimeSeriesSEEG, TimeSeriesEEG, TimeSeriesRegion


class NewDualViewer(BrainViewer):
    """
    New visualizer merging Brain 3D display and EEG lines display.
    Same input as the DualBrainViewer
    """
    _ui_name = "(Work in progress)New Viewer for Time Series in 3D and 2D"
    _ui_subsection = "new_brain_dual"

    def get_input_tree(self):

        return [{'name': 'time_series', 'label': 'Time Series', 'type': TimeSeries, 'required': True,
                 'conditions': FilterChain(fields=[FilterChain.datatype + '.type',
                                                   FilterChain.datatype + '._has_surface_mapping'],
                                           operations=["in", "=="],
                                           values=[['TimeSeriesEEG', 'TimeSeriesSEEG',
                                                    'TimeSeriesMEG', 'TimeSeriesRegion'], True])},

                {'name': 'projection_surface', 'label': 'Projection Surface', 'type': Surface, 'required': False,
                 'description': 'A surface on which to project the results. When missing, the first EEGCap is taken'
                                'This parameter is ignored when InternalSensors measures.'},

                {'name': 'shell_surface', 'label': 'Shell Surface', 'type': Surface, 'required': False,
                 'description': "Wrapping surface over the internal sensors, to be displayed "
                                "semi-transparently, for visual purposes only."}]

    def populate_surface_fields(self, time_series):
        """
        Prepares the urls from which the client may read the data needed for drawing the surface.
        """

        if isinstance(time_series, TimeSeriesRegion):
            BrainViewer.populate_surface_fields(self, time_series)
            return

        self.one_to_one_map = False
        self.region_map = None
        self.connectivity = None

        if self.surface is None:
            eeg_cap = dao.get_generic_entity(EEGCap, "EEGCap", "type")
            if len(eeg_cap) < 1:
                raise Exception("No EEG Cap Surface found for display!")
            self.surface = eeg_cap[0]

    def retrieve_measure_points_prams(self, time_series):

        if isinstance(time_series, TimeSeriesRegion):
            return BrainViewer.retrieve_measure_points_prams(self, time_series)

        self.measure_points_no = time_series.sensors.number_of_sensors

        if isinstance(time_series, TimeSeriesEEG):
            return prepare_mapped_sensors_as_measure_points_params(self.current_project_id,
                                                                   time_series.sensors, self.surface)

        return prepare_sensors_as_measure_points_params(time_series.sensors)

    def launch(self, time_series, projection_surface=None, shell_surface=None):

        self.surface = projection_surface

        if isinstance(time_series, TimeSeriesSEEG) and shell_surface is None:
            shell_surface = dao.try_load_last_entity_of_type(self.current_project_id, CorticalSurface)

        params = BrainViewer.compute_parameters(self, time_series, shell_surface)
        params.update(EegMonitor().compute_parameters(time_series, is_extended_view=True))

        params['isOneToOneMapping'] = False
        params['brainViewerTemplate'] = 'dual_brain_3d_view.html'

        if isinstance(time_series, TimeSeriesSEEG):
            params['brainViewerTemplate'] = "dual_brain_3d_internal_view.html"
            # Mark as None since we only display shelf face and no point to load these as well
            params['urlVertices'] = None
            params['isSEEG'] = True

        if isinstance(time_series, TimeSeriesRegion):
            params['withTransparency'] = True
        else:
            params['withTransparency'] = False


        return self.build_display_result("new_dual_brain/view", params,
                                         pages=dict(controlPage="new_dual_brain/controls",
                                                    channelsPage="commons/channel_selector.html"))
