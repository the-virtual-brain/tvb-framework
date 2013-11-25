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

import json
from tvb.adapters.visualizers.brain import BrainEEG, BrainViewer, BrainSEEG
from tvb.basic.filters.chain import UIFilter, FilterChain
from tvb.basic.traits.core import KWARG_FILTERS_UI
from tvb.core.adapters.abcdisplayer import ABCDisplayer
from tvb.datatypes.sensors import SensorsEEG, SensorsMEG
from tvb.datatypes.sensors_data import SensorsData, SensorsInternalData
from tvb.datatypes.surfaces import EEGCap
from tvb.datatypes.surfaces_data import SurfaceData


class InternalSensorViewer(ABCDisplayer):
    """
    Sensor visualizer - for visual inspecting imported sensors in TVB.
    """
    _ui_name = "Internal sensor Visualizer"
    _ui_subsection = "sensor"

    def get_input_tree(self):
        return [{'name': 'sensors', 'label': 'Brain surface',
                 'type': SensorsInternalData, 'required': True,
                 'description': ''},
               ]

    def launch(self, sensors):
        # SensorsInternalData is the one with directions only?
        # For seeg sensors we need to include seegbrain.js
        # where drawscene is overwritten by a version that draws needles
        measure_points_info = BrainEEG.get_sensor_measure_points(sensors)

        params = {
            'shelfObject' : BrainViewer.get_default_face(),
            'urlVertices': '', 'urlTriangles': '',
            'urlLines': '[]', 'urlNormals': '',
            'urlMeasurePoints' : measure_points_info[0],
            'urlMeasurePointsLabels' : measure_points_info[1],
            'noOfMeasurePoints' : measure_points_info[2] }

        return self.build_display_result('brain/sensors_seeg', params,
                                         pages={'controlPage': 'brain/sensors_controls'})


    def get_required_memory_size(self):
        return -1



class EegSensorViewer(ABCDisplayer):
    """
    Sensor visualizer - for visual inspecting imported sensors in TVB.
    """
    _ui_name = "EEG sensor Visualizer"
    _ui_subsection = "sensor"

    def get_input_tree(self):
        return [{'name': 'sensors', 'label': 'Brain surface',
                 'type': SensorsEEG, 'required': True,
                 'description': 'The sensors datatype to be viewed'},
                {'name': 'eeg_cap', 'label': 'EEG Cap',
                 'type': EEGCap, 'required': False,
                 'description': 'The EEG Cap surface on which to display the results!'}
               ]

    @staticmethod
    def _compute_surface_params(surface):
        rendering_urls = [json.dumps(url) for url in surface.get_urls_for_rendering()]
        url_vertices, url_normals, url_lines, url_triangles = rendering_urls
        return {'urlVertices': url_vertices,
                'urlTriangles': url_triangles,
                'urlLines': url_lines,
                'urlNormals': url_normals}

    def launch(self, sensors, eeg_cap=None):
        measure_points_info = BrainEEG.compute_sensor_surfacemapped_measure_points(sensors, eeg_cap)

        params = {
            'displayMeasureNodes' : True,
            'shelfObject' : BrainViewer.get_default_face(),
            'urlVertices': '', 'urlTriangles': '',
            'urlLines': '[]', 'urlNormals': '',
            'boundaryURL' : '', 'urlAlphas' : '', 'urlAlphasIndices' : '',
            'urlMeasurePoints' : measure_points_info[0],
            'urlMeasurePointsLabels' : measure_points_info[1],
            'noOfMeasurePoints' : measure_points_info[2] }

        if eeg_cap is not None:
            params.update(self._compute_surface_params(eeg_cap))

        return self.build_display_result("brain/sensors_eeg", params,
                                         pages={"controlPage": "brain/sensors_controls"})


    def get_required_memory_size(self):
        return -1


class MEGSensorViewer(EegSensorViewer):
    """
    Sensor visualizer - for visual inspecting imported sensors in TVB.
    """
    _ui_name = "MEEG sensor Visualizer"
    _ui_subsection = "sensor"

    def get_input_tree(self):
        return [{'name': 'sensors', 'label': 'Brain surface',
                 'type': SensorsMEG, 'required': True,
                 'description': 'The sensors datatype to be viewed'},
                {'name': 'eeg_cap', 'label': 'EEG Cap',
                 'type': EEGCap, 'required': False,
                 'description': 'The EEG Cap surface on which to display the results!'}
               ]