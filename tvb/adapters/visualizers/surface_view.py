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
from tvb.basic.filters.chain import UIFilter, FilterChain
from tvb.basic.traits.core import KWARG_FILTERS_UI
from tvb.core.adapters.abcdisplayer import ABCDisplayer
from tvb.datatypes.surfaces import RegionMapping
from tvb.datatypes.surfaces_data import SurfaceData


class SurfaceViewer(ABCDisplayer):
    """
    SurfaceData visualizer
    """

    _ui_name = "SurfaceData Visualizer"
    def get_input_tree(self):
        ui_filter = UIFilter(linked_elem_name="region_map",
                             linked_elem_field=FilterChain.datatype + "._surface")

        json_ui_filter = json.dumps([ui_filter.to_dict()])

        return [{'name': 'surface', 'label': 'Brain surface',
                 'type': SurfaceData, 'required': True,
                 'description': '',
                 KWARG_FILTERS_UI : json_ui_filter},
                {'name': 'region_map', 'label': 'region mapping',
                 'type': RegionMapping, 'required': False,
                 'description': 'A region map' }]


    def compute_parameters(self, surface, region_map):
        rendering_urls = [json.dumps(url) for url in surface.get_urls_for_rendering(True, region_map)]
        url_vertices, url_normals, url_lines, url_triangles, alphas, alphas_indices = rendering_urls

        if region_map is None:
            measure_points_no = 0
            url_measure_points = ''
            url_measure_points_labels = ''
            boundary_url = ''
        else:
            measure_points_no = region_map.connectivity.number_of_regions
            url_measure_points = self.paths2url(region_map.connectivity, 'centres')
            url_measure_points_labels = self.paths2url(region_map.connectivity, 'region_labels')
            boundary_url = surface.get_url_for_region_boundaries(region_map)

        return dict(title="Surface Viewer", urlVertices=url_vertices,
                    urlTriangles=url_triangles, urlLines=url_lines,
                    urlNormals=url_normals, urlAlphas=alphas, urlAlphasIndices=alphas_indices,
                    noOfMeasurePoints=measure_points_no, urlMeasurePoints=url_measure_points,
                    urlMeasurePointsLabels=url_measure_points_labels, boundaryURL=boundary_url,
                    extended_view=False, isOneToOneMapping=False, hasRegionMap=region_map is not None)

    def launch(self, surface, region_map=None):
        params = self.compute_parameters(surface, region_map)
        return self.build_display_result("brain/surface_view", params, pages={"controlPage":"brain/surface_viewer_controls"})

    def get_required_memory_size(self):
        return -1