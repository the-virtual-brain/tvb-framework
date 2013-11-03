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
.. moduleauthor:: Ionel Ortelecan <ionel.ortelecan@codemart.ro>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""

import json
import numpy
from tvb.adapters.visualizers.eeg_monitor import EegMonitor
from tvb.basic.filters.chain import FilterChain
from tvb.core.entities.storage import dao
from tvb.core.adapters.abcdisplayer import ABCDisplayer
from tvb.datatypes.surfaces import RegionMapping, EEGCap, FaceSurface
from tvb.datatypes.time_series import TimeSeries, TimeSeriesSurface, TimeSeriesSEEG


MAX_MEASURE_POINTS_LENGTH = 235



class BrainViewer(ABCDisplayer):
    """
    Interface between the 3D view of the Brain Cortical Surface and TVB framework. 
    This viewer will build the required parameter dictionary that will be sent to the HTML / JS for further processing, 
    having as end result a brain surface plus activity that will be displayed in 3D.
    """
    _ui_name = "Brain Activity Visualizer"
    PAGE_SIZE = 500


    def get_input_tree(self):
        return [{'name': 'time_series', 'label': 'Time Series (Region or Surface)',
                 'type': TimeSeries, 'required': True,
                 'conditions': FilterChain(fields=[FilterChain.datatype + '.type',
                                                   FilterChain.datatype + '._nr_dimensions'],
                                           operations=["in", "=="],
                                           values=[['TimeSeriesRegion', 'TimeSeriesSurface'], 4]),
                 'description': 'Depending on the simulation length and your browser capabilities, you might experience'
                                ' after multiple runs, browser crashes. In such cases, it is recommended to empty the'
                                ' browser cache and try again. Sorry for the inconvenience.'}]


    def get_required_memory_size(self, time_series):
        """
        Return the required memory to run this algorithm.
        """
        overall_shape = time_series.read_data_shape()
        #Assume one page doesn't get 'dumped' in time and maybe two consecutive pages will be in the same 
        #time in memory.
        used_shape = (overall_shape[0] / (self.PAGE_SIZE * 2.0), overall_shape[1], overall_shape[2], overall_shape[3])
        input_size = numpy.prod(used_shape) * 8.0
        return input_size


    def launch(self, time_series):
        """ Build visualizer's page. """
        params = self.compute_parameters(time_series)
        return self.build_display_result("brain/view", params, pages=dict(controlPage="brain/controls"))


    def generate_preview(self, time_series, figure_size=None):
        """ Generate the preview for the burst page """
        params = self.compute_preview_parameters(time_series)
        normalization_factor = figure_size[0] / 800
        if figure_size[1] / 600 < normalization_factor:
            normalization_factor = figure_size[1] / 600
        params['width'] = figure_size[0] * normalization_factor
        params['height'] = figure_size[1] * normalization_factor
        return self.build_display_result("brain/portlet_preview", params, pages=dict())


    def _prepare_surface_urls(self, time_series):
        """
        Prepares the urls from which the client may read the data needed for drawing the surface.
        """
        one_to_one_map = isinstance(time_series, TimeSeriesSurface)
        if not one_to_one_map:
            region_map = dao.get_generic_entity(RegionMapping, time_series.connectivity.gid, '_connectivity')
            if len(region_map) < 1:
                raise Exception("No Mapping Surface found for display!")
            region_map = region_map[0]
            surface = region_map.surface
        else:
            region_map = None
            self.PAGE_SIZE /= 10
            surface = time_series.surface

        if surface is None:
            raise Exception("No not-none Mapping Surface found for display!")

        url_vertices, url_normals, url_lines, url_triangles, alphas, alphas_indices = surface.get_urls_for_rendering(
            True, region_map)
        return one_to_one_map, url_vertices, url_normals, url_lines, url_triangles, alphas, alphas_indices
    
    
    def _get_url_for_region_boundaries(self, time_series):
        one_to_one_map = isinstance(time_series, TimeSeriesSurface)
        if not one_to_one_map and hasattr(time_series, 'connectivity'):
            region_map = dao.get_generic_entity(RegionMapping, time_series.connectivity.gid, '_connectivity')
            if len(region_map) < 1:
                raise Exception("No Mapping Surface found for display!")
            region_map = region_map[0]
            surface = region_map.surface
            return surface.get_url_for_region_boundaries(region_map)
        else:
            return ''


    def compute_preview_parameters(self, time_series):

        one_to_one_map, url_vertices, url_normals, url_lines, url_triangles, \
            alphas, alphas_indices = self._prepare_surface_urls(time_series)

        _, _, measure_points_no = self._retrieve_measure_points(time_series)
        min_val, max_val = time_series.get_min_max_values()
        legend_labels = self._compute_legend_labels(min_val, max_val)

        return dict(urlVertices=json.dumps(url_vertices), urlTriangles=json.dumps(url_triangles),
                    urlLines=json.dumps(url_lines), urlNormals=json.dumps(url_normals),
                    alphas=json.dumps(alphas), alphas_indices=json.dumps(alphas_indices),
                    base_activity_url=ABCDisplayer.VISUALIZERS_URL_PREFIX + time_series.gid,
                    isOneToOneMapping=one_to_one_map, minActivity=min_val, maxActivity=max_val,
                    minActivityLabels=legend_labels, noOfMeasurePoints=measure_points_no)


    def compute_parameters(self, time_series):
        """
        Create the required parameter dictionary for the HTML/JS viewer.

        :rtype: `dict`
        :raises Exception: when
                    * number of measure points exceeds the maximum allowed
                    * a Face object cannot be found in database

        """
        one_to_one_map, url_vertices, url_normals, url_lines, url_triangles, \
            alphas, alphas_indices = self._prepare_surface_urls(time_series)

        measure_points, measure_points_labels, measure_points_no = self._retrieve_measure_points(time_series)
        if (not one_to_one_map) and (measure_points_no > MAX_MEASURE_POINTS_LENGTH):
            raise Exception("Max number of measure points " + str(MAX_MEASURE_POINTS_LENGTH) + " exceeded.")

        base_activity_url, time_urls = self._prepare_data_slices(time_series)
        min_val, max_val = time_series.get_min_max_values()
        legend_labels = self._compute_legend_labels(min_val, max_val)

        face_surface = dao.get_generic_entity(FaceSurface, "FaceSurface", "type")
        if len(face_surface) == 0:
            raise Exception("No face object found in database.")
        face_vertices, face_normals, _, face_triangles = face_surface[0].get_urls_for_rendering()
        face_object = json.dumps([face_vertices, face_normals, face_triangles])

        data_shape = time_series.read_data_shape()
        state_variables = time_series.labels_dimensions.get(time_series.labels_ordering[1], [])

        boundary_url = self._get_url_for_region_boundaries(time_series)

        return dict(title="Cerebral Activity", isOneToOneMapping=one_to_one_map,
                    urlVertices=json.dumps(url_vertices), urlTriangles=json.dumps(url_triangles), 
                    urlLines=json.dumps(url_lines), urlNormals=json.dumps(url_normals), 
                    urlMeasurePointsLabels=measure_points_labels, measure_points=measure_points, 
                    noOfMeasurePoints=measure_points_no, alphas=json.dumps(alphas), 
                    alphas_indices=json.dumps(alphas_indices), base_activity_url=base_activity_url,
                    time=json.dumps(time_urls), minActivity=min_val, maxActivity=max_val, 
                    minActivityLabels=legend_labels, labelsStateVar=state_variables, labelsModes=range(data_shape[3]), 
                    extended_view=False, shelfObject=face_object, time_series=time_series, pageSize=self.PAGE_SIZE, 
                    boundary_url=boundary_url)


    @staticmethod
    def _prepare_mappings(mappings_dict):
        """
        Get full mapping dictionary between the original vertices and multiple slices (for WebGL compatibility).
        """
        prepared_mappings = []
        for key in mappings_dict:
            this_mappings = []
            vert_map_dict = mappings_dict[key]
            vertices_indexes = vert_map_dict['indices']
            this_mappings.append(vertices_indexes[0].tolist())
            for i in range(1, len(vertices_indexes)):
                if vertices_indexes[i][0] == vertices_indexes[i][1]:
                    this_mappings.append(vertices_indexes[i][0])
                else:
                    for index in range(vertices_indexes[i][0], vertices_indexes[i][1] + 1):
                        this_mappings.append(index)
            prepared_mappings.append(this_mappings)
        return prepared_mappings


    def _retrieve_measure_points(self, time_series):
        """
        To be overwritten method, for retrieving the measurement points (region centers, EEG sensors).
        """
        if isinstance(time_series, TimeSeriesSurface):
            return [], [], 0
        measure_points = self.paths2url(time_series.connectivity, 'centres')
        measure_points_labels = self.paths2url(time_series.connectivity, 'region_labels')
        measure_points_no = time_series.connectivity.number_of_regions
        return measure_points, measure_points_labels, measure_points_no


    @staticmethod
    def _compute_legend_labels(min_val, max_val, nr_labels=5, min_nr_dec=3):
        """
        Compute rounded labels for MIN and MAX values such that decimals will show a difference between them.
        """
        min_integer, min_decimals = str(min_val).split('.')
        max_integer, max_decimals = str(max_val).split('.')
        idx = min_nr_dec
        if len(min_decimals) < min_nr_dec or len(max_decimals) < min_nr_dec:
            processed_min_val = float(min_val)
            processed_max_val = float(max_val)
        elif min_integer != max_integer:
            processed_min_val = float(min_integer + '.' + min_decimals[:min_nr_dec])
            processed_max_val = float(max_integer + '.' + max_decimals[:min_nr_dec])
        else:
            for idx, val in enumerate(min_decimals):
                if idx < len(max_decimals) or val != max_decimals[idx]:
                    break
            processed_min_val = float(min_integer + '.' + min_decimals[:idx])
            processed_max_val = float(max_integer + '.' + max_decimals[:idx])
        value_diff = (processed_max_val - processed_min_val) / (nr_labels + 1)
        inter_values = [round(processed_min_val + value_diff * i, idx) for i in reversed(range(1, (nr_labels + 1)))]
        return [processed_max_val] + inter_values + [processed_min_val]


    def _prepare_data_slices(self, time_series):
        """
        Prepare data URL for retrieval with slices of timeSeries activity and Time-Line.
        :returns: [activity_urls], [timeline_urls]
                 Currently timeline_urls has just one value, as on client is loaded entirely anyway.
        """
        overall_shape = time_series.read_data_shape()

        activity_base_url = ABCDisplayer.VISUALIZERS_URL_PREFIX + time_series.gid
        time_urls = [self.paths2url(time_series, 'read_time_page',
                                    parameter="current_page=0;page_size=" + str(overall_shape[0]))]
        return activity_base_url, time_urls


class BrainEEG(BrainViewer):
    """
    Visualizer merging Brain 3D display and EEG lines display.
    """
    _ui_name = "Brain EEG Activity in 3D and 2D"
    _ui_subsection = "brain_eeg"

    def get_input_tree(self):
        
        return [{'name': 'surface_activity', 'label': 'Time Series (EEG or MEG)',
                 'type': TimeSeries, 'required': True,
                 'conditions': FilterChain(fields=[FilterChain.datatype + '.type'],
                                           operations=["in"],
                                           values=[['TimeSeriesEEG', 'TimeSeriesMEG']]),
                 'description': 'Depending on the simulation length and your browser capabilities, you might experience'
                                ' after multiple runs, browser crashes. In such cases, it is recommended to empty the'
                                ' browser cache and try again. Sorry for the inconvenience.'},
                {'name': 'eeg_cap', 'label': 'EEG Cap',
                 'type': EEGCap, 'required': False,
                 'description': 'The EEG Cap surface on which to display the results!'}]
        
        
    def _retrieve_measure_points(self, surface_activity):
        """
        Overwrite, and compute sensors positions after mapping or skin surface of unit-vectors

        :returns: measure points, measure points labels, measure points number
        :rtype: tuple
        """
        measure_points, measure_points_no = None, 0
        if not hasattr(self, 'eeg_cap') or self.eeg_cap is None:
            cap_eeg = dao.get_generic_entity(EEGCap, "EEGCap", "type")
            if len(cap_eeg) < 1:
                measure_points = self.paths2url(surface_activity.sensors, 'locations')
                measure_points_no = surface_activity.sensors.number_of_sensors
                self.eeg_cap = None
            else:
                self.eeg_cap = cap_eeg[0]
        if self.eeg_cap:
            sensor_locations = surface_activity.sensors.sensors_to_surface(self.eeg_cap)[1]
            measure_points = json.dumps(sensor_locations.tolist())
            measure_points_no = - surface_activity.sensors.number_of_sensors

        measure_points_labels = self.paths2url(surface_activity.sensors, 'labels')
        return measure_points, measure_points_labels, measure_points_no


    def launch(self, surface_activity, eeg_cap=None):
        """
        Overwrite Brain Visualizer launch and extend functionality,
        by adding a Monitor set of parameters near.
        """
        self.eeg_cap = eeg_cap
        params = BrainViewer.compute_parameters(self, surface_activity)
        params.update(EegMonitor().compute_parameters(surface_activity))
        params['extended_view'] = True
        params['isOneToOneMapping'] = False
        params['brainViewerTemplate'] = 'view.html'
        return self.build_display_result("brain/extendedview", params,
                                         pages=dict(controlPage="brain/extendedcontrols",
                                                    channelsPage="commons/channel_selector.html"))


    def _prepare_surface_urls(self, time_series):
        """
        Prepares the urls from which the client may read the data needed for drawing the surface.
        """
        one_to_one_map = False
        if self.eeg_cap is None:
            eeg_cap = dao.get_generic_entity(EEGCap, "EEGCap", "type")
            if len(eeg_cap) < 1:
                raise Exception("No EEG Cap Surface found for display!")
            self.eeg_cap = eeg_cap[0]
        url_vertices, url_normals, url_lines, url_triangles = self.eeg_cap.get_urls_for_rendering()
        alphas = []
        alphas_indices = []

        return one_to_one_map, url_vertices, url_normals, url_lines, url_triangles, alphas, alphas_indices


class BrainSEEG(BrainEEG):
    """
    Visualizer merging Brain 3D display and MEG lines display.
    """
    _ui_name = "Brain SEEG Activity in 3D and 2D"
    _ui_subsection = "brain_seeg"


    def get_input_tree(self):
        return [{'name': 'surface_activity', 'label': 'SEEG activity',
                 'type': TimeSeriesSEEG, 'required': True,
                 'description': 'Results after SEEG Monitor are expected!'}]
        
    
    def _retrieve_measure_points(self, surface_activity):
        """
        Overwrite, and compute sensors positions after mapping or skin surface of unit-vectors

        :returns: measure points, measure points labels, measure points number
        :rtype: tuple
        """
        measure_points = self.paths2url(surface_activity.sensors, 'locations')
        measure_points_no = surface_activity.sensors.number_of_sensors
        measure_points_labels = self.paths2url(surface_activity.sensors, 'labels')
        return measure_points, measure_points_labels, measure_points_no
    
    
    def launch(self, surface_activity, eeg_cap=None):
        result_params = BrainEEG.launch(self, surface_activity)
        result_params['brainViewerTemplate'] = "seeg_view.html"
        # Mark as None since we only display shelf face and no point to load these as well
        result_params['urlVertices'] = None
        result_params['isSEEG'] = True
        return result_params
        