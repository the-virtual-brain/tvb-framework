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
.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
"""

import json
import numpy
from tvb.basic.logger.builder import get_logger

from tvb.core.adapters.abcadapter import ABCAdapterForm
from tvb.core.adapters.abcdisplayer import ABCDisplayer, URLGenerator
from tvb.core.entities.model.datatypes.graph import ConnectivityMeasureIndex
from tvb.core.entities.model.datatypes.region_mapping import RegionMappingIndex
from tvb.core.entities.model.datatypes.surface import SurfaceIndex
from tvb.core.entities.storage import dao
from tvb.core.neotraits._forms import DataTypeSelectField
from tvb.datatypes.surfaces import SPLIT_PICK_MAX_TRIANGLE, KEY_VERTICES, KEY_START, Surface

LOG = get_logger(__name__)


def ensure_shell_surface(project_id, shell_surface=None, preferred_type='Face Surface'):
    if shell_surface is None:
        shell_surface = dao.try_load_last_surface_of_type(project_id, preferred_type)

        if not shell_surface:
            # TODO: should this throw exception for other viewers?
            LOG.warning('No object of type %s found in current project.' % preferred_type)

    return shell_surface


class SurfaceURLGenerator(URLGenerator):

    @staticmethod
    def get_urls_for_rendering(surface_h5, region_mapping=None):
        """
        Compose URLs for the JS code to retrieve a surface from the UI for rendering.
        """
        url_vertices = []
        url_triangles = []
        url_normals = []
        url_lines = []
        url_region_map = []
        gid = surface_h5.gid.load().hex
        for i in range(surface_h5.number_of_split_slices.load()):
            param = "slice_number=" + str(i)
            url_vertices.append(URLGenerator.build_h5_url(gid, 'get_vertices_slice', parameter=param, flatten=True))
            url_triangles.append(URLGenerator.build_h5_url(gid, 'get_triangles_slice', parameter=param, flatten=True))
            url_lines.append(URLGenerator.build_h5_url(gid, 'get_lines_slice', parameter=param, flatten=True))
            url_normals.append(
                URLGenerator.build_h5_url(gid, 'get_vertex_normals_slice', parameter=param, flatten=True))
            if region_mapping is None:
                continue

            start_idx, end_idx = surface_h5._get_slice_vertex_boundaries(i)
            url_region_map.append(URLGenerator.paths2url(region_mapping.gid.load().hex, "get_region_mapping_slice",
                                                         flatten=True,
                                                         parameter="start_idx=" + str(start_idx) + " ;end_idx=" + str(
                                                             end_idx)))

        if region_mapping:
            return url_vertices, url_normals, url_lines, url_triangles, url_region_map
        return url_vertices, url_normals, url_lines, url_triangles, None

    @staticmethod
    def get_urls_for_pick_rendering(surface_h5):
        """
        Compose URLS for the JS code to retrieve a surface for picking.
        """
        vertices = []
        triangles = []
        normals = []
        number_of_triangles = surface_h5.number_of_triangles.load()
        number_of_split = number_of_triangles // SPLIT_PICK_MAX_TRIANGLE
        if number_of_triangles % SPLIT_PICK_MAX_TRIANGLE > 0:
            number_of_split += 1

        gid = surface_h5.gid.load().hex
        for i in range(number_of_split):
            param = "slice_number=" + str(i)
            vertices.append(URLGenerator.build_h5_url(gid, 'get_pick_vertices_slice', parameter=param, flatten=True))
            triangles.append(URLGenerator.build_h5_url(gid, 'get_pick_triangles_slice', parameter=param, flatten=True))
            normals.append(
                URLGenerator.build_h5_url(gid, 'get_pick_vertex_normals_slice', parameter=param, flatten=True))

        return vertices, normals, triangles

    @staticmethod
    def get_url_for_region_boundaries(surface_h5, region_mapping, adapter_id):
        surface_gid = surface_h5.gid.load().hex
        region_mapping_gid = region_mapping.gid.load().hex
        return URLGenerator.build_url(surface_gid, 'generate_region_boundaries', adapter_id=adapter_id,
                                      parameter='region_mapping_gid=' + region_mapping_gid)


class BaseSurfaceViewerForm(ABCAdapterForm):

    def __init__(self, prefix='', project_id=None):
        super(BaseSurfaceViewerForm, self).__init__(prefix, project_id)
        self.region_map = DataTypeSelectField(RegionMappingIndex, self, name='region_map', label='Region mapping',
                                              doc='A region map')
        self.connectivity_measure = DataTypeSelectField(ConnectivityMeasureIndex, self, name='connectivity_measure',
                                                        label='Connectivity measure', doc='A connectivity measure')
        self.shell_surface = DataTypeSelectField(SurfaceIndex, self, name='shell_surface', label='Shell Surface',
                                                 doc='Face surface to be displayed semi-transparently, for orientation only.')

    @staticmethod
    def get_filters():
        return None


class SurfaceViewerForm(BaseSurfaceViewerForm):
    def __init__(self, prefix='', project_id=None):
        # filters_ui = [UIFilter(linked_elem_name="region_map",
        #                        linked_elem_field=FilterChain.datatype + "._surface"),
        #               UIFilter(linked_elem_name="connectivity_measure",
        #                        linked_elem_field=FilterChain.datatype + "._surface")]
        # json_ui_filter = json.dumps([ui_filter.to_dict() for ui_filter in filters_ui])

        super(SurfaceViewerForm, self).__init__(prefix, project_id)
        self.surface = DataTypeSelectField(self.get_required_datatype(), self, name='surface',
                                           required=True, label='Brain surface')

    @staticmethod
    def get_required_datatype():
        return SurfaceIndex

    @staticmethod
    def get_input_name():
        return '_surface'


class SurfaceViewer(ABCDisplayer):
    """
    Static SurfaceData visualizer - for visual inspecting imported surfaces in TVB.
    Optionally it can display associated RegionMapping entities.
    """
    _ui_name = "Surface Visualizer"
    _ui_subsection = "surface"
    form = None

    def get_form(self):
        if not self.form:
            return SurfaceViewerForm
        return self.form

    def set_form(self, form):
        self.form = form

    def get_input_tree(self):
        return None

    def _compute_surface_params(self, surface_h5, region_map=None):
        rendering_urls = []
        # we want the URLs in json
        # But these string are going to be verbatim strings in js source code
        # This means that js will interpret escapes like \" so the json parser gets "
        # Double escape is needed \\"
        for url in SurfaceURLGenerator.get_urls_for_rendering(surface_h5, region_map):
            escaped_url = json.dumps(url).replace('\\', '\\\\')
            rendering_urls.append(escaped_url)
        url_vertices, url_normals, url_lines, url_triangles, url_region_map = rendering_urls

        return dict(urlVertices=url_vertices, urlTriangles=url_triangles, urlLines=url_lines,
                    urlNormals=url_normals, urlRegionMap=url_region_map)

    def _compute_hemispheric_param(self, surface_h5):
        bi_hemispheric = surface_h5.bi_hemispheric.load()
        hemisphere_chunk_mask = surface_h5.get_slices_to_hemisphere_mask()
        return dict(biHemispheric=bi_hemispheric, hemisphereChunkMask=json.dumps(hemisphere_chunk_mask))

    def _compute_measure_points_param(self, surface_h5, region_map):
        if region_map is None:
            measure_points_no = 0
            url_measure_points = ''
            url_measure_points_labels = ''
            boundary_url = ''
        else:
            connectivity_gid = region_map.connectivity.load().hex
            connectivity_index = self.load_entity_by_gid(connectivity_gid)

            measure_points_no = connectivity_index.number_of_regions

            url_measure_points = SurfaceURLGenerator.build_h5_url(connectivity_gid, 'get_centres')
            url_measure_points_labels = SurfaceURLGenerator.build_h5_url(connectivity_gid, 'get_region_labels')

            boundary_url = SurfaceURLGenerator.get_url_for_region_boundaries(surface_h5, region_map,
                                                                             self.stored_adapter.id)

        return dict(noOfMeasurePoints=measure_points_no, urlMeasurePoints=url_measure_points,
                    urlMeasurePointsLabels=url_measure_points_labels, boundaryURL=boundary_url)

    def _compute_measure_param(self, connectivity_measure, measure_points_no):
        if connectivity_measure is None:
            # If there is no measure to show then we what to show the region mapping
            # The client will generate a range signal for this use case.
            min_measure = 0
            max_measure = measure_points_no
            client_measure_url = ''
        else:
            connectivity_measure_shape = connectivity_measure.array_data.shape
            if len(connectivity_measure_shape) != 1:
                raise ValueError("connectivity measure must be 1 dimensional")
            if connectivity_measure_shape[0] != measure_points_no:
                raise ValueError("connectivity measure has %d values but the connectivity has %d "
                                 "regions" % (connectivity_measure_shape[0], measure_points_no))
            min_measure = numpy.min(connectivity_measure.array_data[:])
            max_measure = numpy.max(connectivity_measure.array_data[:])
            # We assume here that the index 0 in the measure corresponds to
            # the region 0 of the region map.
            client_measure_url = SurfaceURLGenerator.build_h5_url(connectivity_measure.gid.load().hex,
                                                                  "get_array_data")

        return dict(minMeasure=min_measure, maxMeasure=max_measure, clientMeasureUrl=client_measure_url)

    def _determine_h5_file_for_inputs(self, index):
        h5_file = None
        if index:
            h5_class, h5_path = self._load_h5_of_gid(index.gid)
            h5_file = h5_class(h5_path)

        return h5_file

    def launch(self, surface, region_map=None, connectivity_measure=None, shell_surface=None,
               title="Surface Visualizer"):

        params = dict(title=title, extended_view=False, isOneToOneMapping=False,
                      hasRegionMap=region_map is not None)

        surface_h5 = self._determine_h5_file_for_inputs(surface)
        rm_h5 = self._determine_h5_file_for_inputs(region_map)
        cm_h5 = self._determine_h5_file_for_inputs(connectivity_measure)

        params.update(self._compute_surface_params(surface_h5, rm_h5))
        params.update(self._compute_hemispheric_param(surface_h5))
        params.update(self._compute_measure_points_param(surface_h5, rm_h5))
        params.update(self._compute_measure_param(cm_h5, params['noOfMeasurePoints']))

        surface_h5.close()
        if rm_h5:
            rm_h5.close()
        if cm_h5:
            cm_h5.close()

        params['shelfObject'] = None
        shell_surface = ensure_shell_surface(self.current_project_id, shell_surface)

        if shell_surface:
            shell_h5 = self._determine_h5_file_for_inputs(shell_surface)
            shell_vertices, shell_normals, _, shell_triangles, _ = SurfaceURLGenerator.get_urls_for_rendering(shell_h5)
            params['shelfObject'] = json.dumps([shell_vertices, shell_normals, shell_triangles])
            shell_h5.close()

        return self.build_display_result("surface/surface_view", params,
                                         pages={"controlPage": "surface/surface_viewer_controls"})

    def get_required_memory_size(self):
        return -1


class RegionMappingViewerForm(BaseSurfaceViewerForm):

    def __init__(self, prefix='', project_id=None):
        super(RegionMappingViewerForm, self).__init__(prefix, project_id)
        self.region_map.required = True

    @staticmethod
    def get_required_datatype():
        return RegionMappingIndex

    @staticmethod
    def get_input_name():
        return '_region_map'


class RegionMappingViewer(SurfaceViewer):
    """
    This is a viewer for RegionMapping DataTypes.
    It reuses almost everything from SurfaceViewer, but it make required another input param.
    """
    _ui_name = "Region Mapping Visualizer"
    _ui_subsection = "surface"
    form = None

    def get_form(self):
        if not self.form:
            return RegionMappingViewerForm
        return self.form

    def launch(self, region_map, connectivity_measure=None, shell_surface=None):
        region_map_h5 = self._determine_h5_file_for_inputs(region_map)
        surface_gid = region_map_h5.surface.load().hex
        surface_index = dao.get_datatype_by_gid(surface_gid)
        region_map_h5.close()

        return SurfaceViewer.launch(self, surface_index, region_map, connectivity_measure, shell_surface,
                                    title=RegionMappingViewer._ui_name)


class ConnectivityMeasureOnSurfaceViewerForm(BaseSurfaceViewerForm):

    def __init__(self, prefix='', project_id=None):
        super(ConnectivityMeasureOnSurfaceViewerForm, self).__init__(prefix, project_id)
        self.connectivity_measure.required = True

    @staticmethod
    def get_required_datatype():
        return ConnectivityMeasureIndex

    @staticmethod
    def get_input_name():
        return '_connectivity_measure'


class ConnectivityMeasureOnSurfaceViewer(SurfaceViewer):
    """
    This displays a connectivity measure on a surface via a RegionMapping
    It reuses almost everything from SurfaceViewer, but it make required another input param.
    """
    _ui_name = "Connectivity Measure Surface Visualizer"
    _ui_subsection = "surface"
    form = None

    def get_form(self):
        if not self.form:
            return ConnectivityMeasureOnSurfaceViewerForm
        return self.form

    def launch(self, connectivity_measure, region_map=None, shell_surface=None):
        connectivity_measure_h5 = self._determine_h5_file_for_inputs(connectivity_measure)
        cm_connectivity_gid = connectivity_measure_h5.connectivity.load().hex
        cm_connectivity_index = dao.get_datatype_by_gid(cm_connectivity_gid)
        connectivity_measure_h5.close()

        surface_index = None

        if not region_map:
            region_maps = dao.get_generic_entity(RegionMappingIndex, cm_connectivity_gid, 'connectivity_id')
            if region_maps:
                region_map = region_maps[0]
                # else: todo fallback on any region map with the right number of nodes

        if region_map:
            region_map_h5 = self._determine_h5_file_for_inputs(region_map)
            rm_connectivity_gid = region_map_h5.connectivity.load().hex
            rm_connectivity_index = dao.get_datatype_by_gid(rm_connectivity_gid)
            surface_gid = region_map_h5.surface.load().hex
            surface_index = dao.get_datatype_by_gid(surface_gid)
            region_map_h5.close()

            if rm_connectivity_index.number_of_regions != cm_connectivity_index.number_of_regions:
                region_maps = dao.get_generic_entity(RegionMappingIndex, cm_connectivity_gid, 'connectivity_id')
                if region_maps:
                    region_map = region_maps[0]

        return SurfaceViewer.launch(self, surface_index, region_map, connectivity_measure, shell_surface,
                                    title=self._ui_name)
