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
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""
import json
import os
import sys
from threading import Lock
from abc import ABCMeta
import numpy
from tvb.basic.arguments_serialisation import preprocess_space_parameters, postprocess_voxel_ts, \
    preprocess_time_parameters
from tvb.datatypes.surfaces import Surface, KEY_VERTICES, KEY_START
from tvb.datatypes.time_series import prepare_time_slice
from tvb.core.adapters.abcadapter import ABCSynchronous
from tvb.core.adapters.exceptions import LaunchException
from tvb.core.entities.file.datatypes.connectivity_h5 import ConnectivityH5
from tvb.core.entities.file.datatypes.sensors_h5 import SensorsH5
from tvb.core.entities.file.datatypes.time_series import TimeSeriesRegionH5, TimeSeriesSensorsH5
from tvb.interfaces.neocom._h5loader import DirLoader
from tvb.interfaces.neocom.config import registry

LOCK_CREATE_FIGURE = Lock()


class URLGenerator(object):
    FLOW = 'flow'
    INVOKE_ADAPTER = 'invoke_adapter'
    H5_FILE = 'read_from_h5_file'
    DATATYPE_ATTRIBUTE = 'read_datatype_attribute'

    @staticmethod
    def build_base_h5_url(entity_gid):
        url_regex = '/{}/{}/{}'
        return url_regex.format(URLGenerator.FLOW, URLGenerator.H5_FILE, entity_gid)

    @staticmethod
    def build_url(entity_gid, method_name, adapter_id, parameter=None):
        url_regex = '/{}/{}/{}/{}/{}'
        url = url_regex.format(URLGenerator.FLOW, URLGenerator.INVOKE_ADAPTER, adapter_id, method_name, entity_gid)

        if parameter is not None:
            url += "?" + str(parameter)

        return url


    @staticmethod
    def build_h5_url(entity_gid, method_name, flatten=False, datatype_kwargs=None, parameter=None):
        json_kwargs = json.dumps(datatype_kwargs)

        url_regex = '/{}/{}/{}/{}/{}/{}'
        url = url_regex.format(URLGenerator.FLOW, URLGenerator.H5_FILE, entity_gid, method_name, flatten, json_kwargs)

        if parameter is not None:
            url += "?" + str(parameter)

        return url


    @staticmethod
    def paths2url(datatype_gid, attribute_name, flatten=False, parameter=None):
        """
        Prepare a File System Path for passing into an URL.
        """
        url_regex = '/{}/{}/{}/{}/{}'
        url = url_regex.format(URLGenerator.FLOW, URLGenerator.DATATYPE_ATTRIBUTE, datatype_gid, attribute_name, flatten)

        if parameter is not None:
            url += "?" + str(parameter)

        return url


class ABCDisplayer(ABCSynchronous):
    """
    Abstract class, for marking Adapters used for UI display only.
    """
    __metaclass__ = ABCMeta
    KEY_CONTENT_MODULE = "keyContentModule"
    KEY_CONTENT = "mainContent"
    KEY_IS_ADAPTER = "isAdapter"
    PARAM_FIGURE_SIZE = 'figure_size'
    VISUALIZERS_ROOT = ''
    VISUALIZERS_URL_PREFIX = ''


    def get_output(self):
        return []


    def generate_preview(self, **kwargs):
        """
        Should be implemented by all visualizers that can be used by portlets.
        """
        raise LaunchException("%s used as Portlet but doesn't implement 'generate_preview'" % self.__class__)


    def _prelaunch(self, operation, uid=None, available_disk_space=0, **kwargs):
        """
        Shortcut in case of visualization calls.
        """
        self.operation_id = operation.id
        self.current_project_id = operation.project.id
        self.user_id = operation.fk_launched_by
        self.storage_path = self.file_handler.get_project_folder(operation.project, str(operation.id))

        return self.launch(**kwargs), 0


    def get_required_disk_size(self, **kwargs):
        """
        Visualizers should no occupy any additional disk space.
        """
        return 0


    def build_display_result(self, template, parameters, pages=None):
        """
        Helper method for building the result of the ABCDisplayer.
        :param template : path towards the HTML template to display. It can be absolute path, or relative
        :param parameters : dictionary with parameters for "template"
        :param pages : dictionary of pages to be used with <xi:include>
        """
        module_ref = __import__(self.VISUALIZERS_ROOT, globals(), locals(), ["__init__"])
        relative_path = os.path.dirname(module_ref.__file__)

        ### We still need the relative file path into desktop client
        if os.path.isabs(template):
            parameters[self.KEY_CONTENT_MODULE] = ""
        else:
            content_module = self.VISUALIZERS_ROOT + "."
            content_module = content_module + template.replace("/", ".")
            parameters[self.KEY_CONTENT_MODULE] = content_module

        if not os.path.isabs(template):
            template = os.path.join(relative_path, template)
        if not os.path.isabs(template):
            template = os.path.join(os.path.dirname(sys.executable), template)
        if pages:
            for key, value in pages.items():
                if value is not None:
                    if not os.path.isabs(value):
                        value = os.path.join(relative_path, value)
                    if not os.path.isabs(value):
                        value = os.path.join(os.path.dirname(sys.executable), value)
                parameters[key] = value
        parameters[self.KEY_CONTENT] = template
        parameters[self.KEY_IS_ADAPTER] = True

        return parameters


    @staticmethod
    def get_one_dimensional_list(list_of_elements, expected_size, error_msg):
        """
        Used for obtaining a list of 'expected_size' number of elements from the
        list 'list_of_elements'. If the list 'list_of_elements' doesn't have 
        sufficient elements then an exception will be thrown.

        list_of_elements - a list of one or two dimensions
        expected_size - the number of elements that should have the returned list
        error_msg - the message that will be used for the thrown exception.
        """
        if len(list_of_elements) > 0 and isinstance(list_of_elements[0], list):
            if len(list_of_elements[0]) < expected_size:
                raise LaunchException(error_msg)
            return list_of_elements[0][:expected_size]
        else:
            if len(list_of_elements) < expected_size:
                raise LaunchException(error_msg)
            return list_of_elements[:expected_size]


    #TODO: remove methods that build urls
    def build_url(self, method_name, entity_gid, parameter=None):
        url ='/flow/invoke_adapter/' + str(self.stored_adapter.id) + '/' + method_name + '/' + entity_gid

        if parameter is not None:
            url += "?" + str(parameter)

        return url

    def build_h5_url(self, entity_gid, method_name, parameter=None):
        url = '/flow/read_from_h5_file/' + entity_gid + '/' + method_name

        if parameter is not None:
            url += "?" + str(parameter)

        return url

    @staticmethod
    def paths2url(datatype_gid, attribute_name, flatten=False, parameter=None):
        """
        Prepare a File System Path for passing into an URL.
        """
        url = ABCDisplayer.VISUALIZERS_URL_PREFIX + datatype_gid + '/' + attribute_name + '/' + str(flatten)

        if parameter is not None:
            url += "?" + str(parameter)
        return url


    def build_template_params_for_subselectable_datatype(self, sub_selectable):
        """
        creates a template dict with the initial selection to be
        displayed in a time series viewer
        """
        return {'measurePointsSelectionGID': sub_selectable.gid.load().hex,
                'initialSelection': self.get_default_selection(sub_selectable),
                'groupedLabels': self.get_grouped_space_labels(sub_selectable)}


    @staticmethod
    def dump_with_precision(xs, precision=3):
        """
        Dump a list of numbers into a string, each at the specified precision.
        """
        format_str = "%0." + str(precision) + "g"
        return "[" + ",".join(format_str % s for s in xs) + "]"

    def _load_h5_of_gid(self, entity_gid):
        entity_index = self.load_entity_by_gid(entity_gid)
        loader = DirLoader(os.path.join(os.path.dirname(self.storage_path), str(entity_index.fk_from_operation)))
        entity_h5_class = registry.get_h5file_for_index(type(entity_index))
        entity_h5_path = loader.path_for(entity_h5_class, entity_gid)
        return entity_h5_class, entity_h5_path

    def get_voxel_time_series(self, entity_gid, **kwargs):
        """
        Retrieve for a given voxel (x,y,z) the entire timeline.

        :param x: int coordinate
        :param y: int coordinate
        :param z: int coordinate

        :return: A complex dictionary with information about current voxel.
                The main part will be a vector with all the values over time from the x,y,z coordinates.
        """

        ts_h5_class, ts_h5_path = self._load_h5_of_gid(entity_gid)

        with ts_h5_class(ts_h5_path) as ts_h5:
            if ts_h5_class is TimeSeriesRegionH5:
                return self._get_voxel_time_series_region(ts_h5, **kwargs)

            return ts_h5.get_voxel_time_series(**kwargs)

    def _get_voxel_time_series_region(self, ts_h5, x, y, z, var=0, mode=0):
        region_mapping_volume_gid = ts_h5.region_mapping_volume.load()
        if region_mapping_volume_gid is None:
            raise Exception("Invalid method called for TS without Volume Mapping!")

        volume_rm_h5_class, volume_rm_h5_path = self._load_h5_of_gid(region_mapping_volume_gid.hex)
        volume_rm_h5 = volume_rm_h5_class(volume_rm_h5_path)

        volume_rm_shape = volume_rm_h5.array_data.shape
        x, y, z = preprocess_space_parameters(x, y, z, volume_rm_shape[0], volume_rm_shape[1], volume_rm_shape[2])
        idx_slices = slice(x, x + 1), slice(y, y + 1), slice(z, z + 1)

        idx = int(volume_rm_h5.array_data[idx_slices])

        time_length = ts_h5.data.shape[0]
        var, mode = int(var), int(mode)
        voxel_slices = prepare_time_slice(time_length), slice(var, var + 1), slice(idx, idx + 1), slice(mode, mode + 1)

        connectivity_gid = volume_rm_h5.connectivity.load()
        connectivity_h5_class, connectivity_h5_path = self._load_h5_of_gid(connectivity_gid.hex)
        connectivity_h5 = connectivity_h5_class(connectivity_h5_path)
        label = connectivity_h5.region_labels.load()[idx]

        background, back_min, back_max = None, None, None
        if idx < 0:
            back_min, back_max = ts_h5.get_min_max_values()
            background = numpy.ones((time_length, 1)) * ts_h5.out_of_range(back_min)
            label = 'background'

        volume_rm_h5.close()
        connectivity_h5.close()

        result = postprocess_voxel_ts(self, voxel_slices, background, back_min, back_max, label)
        return result

    def get_volume_view(self, entity_gid, **kwargs):
        ts_h5_class, ts_h5_path = self._load_h5_of_gid(entity_gid)
        with ts_h5_class(ts_h5_path) as ts_h5:
            if ts_h5_class is TimeSeriesRegionH5:
                return self._get_volume_view_region(ts_h5, **kwargs)

            return ts_h5.get_volume_view(**kwargs)

    def _get_volume_view_region(self, ts_h5, from_idx, to_idx, x_plane, y_plane, z_plane, var=0, mode=0):
        """
        Retrieve 3 slices through the Volume TS, at the given X, y and Z coordinates, and in time [from_idx .. to_idx].

        :param from_idx: int This will be the limit on the first dimension (time)
        :param to_idx: int Also limit on the first Dimension (time)
        :param x_plane: int coordinate
        :param y_plane: int coordinate
        :param z_plane: int coordinate

        :return: An array of 3 Matrices 2D, each containing the values to display in planes xy, yz and xy.
        """
        region_mapping_volume_gid = ts_h5.region_mapping_volume.load()

        if region_mapping_volume_gid is None:
            raise Exception("Invalid method called for TS without Volume Mapping!")

        volume_rm_h5_class, volume_rm_h5_path = self._load_h5_of_gid(region_mapping_volume_gid.hex)
        volume_rm_h5 = volume_rm_h5_class(volume_rm_h5_path)
        volume_rm_shape = volume_rm_h5.array_data.shape

        # Work with space inside Volume:
        x_plane, y_plane, z_plane = preprocess_space_parameters(x_plane, y_plane, z_plane, volume_rm_shape[0],
                                                                volume_rm_shape[1], volume_rm_shape[2])
        var, mode = int(var), int(mode)
        slice_x, slice_y, slice_z = volume_rm_h5.get_volume_slice(x_plane, y_plane, z_plane)

        # Read from the current TS:
        from_idx, to_idx, current_time_length = preprocess_time_parameters(from_idx, to_idx, ts_h5.data.shape[0])
        no_of_regions = ts_h5.data.shape[2]
        time_slices = slice(from_idx, to_idx), slice(var, var + 1), slice(no_of_regions), slice(mode, mode + 1)

        min_signal = ts_h5.get_min_max_values()[0]
        regions_ts = ts_h5.read_data_slice(time_slices)[:, 0, :, 0]
        regions_ts = numpy.hstack((regions_ts, numpy.ones((current_time_length, 1)) * ts_h5.out_of_range(min_signal)))

        volume_rm_h5.close()

        # Index from TS with the space mapping:
        result_x, result_y, result_z = [], [], []

        for i in range(0, current_time_length):
            result_x.append(regions_ts[i][slice_x].tolist())
            result_y.append(regions_ts[i][slice_y].tolist())
            result_z.append(regions_ts[i][slice_z].tolist())

        return [result_x, result_y, result_z]

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

    def generate_region_boundaries(self, surface_gid, region_mapping_gid):
        """
        Return the full region boundaries, including: vertices, normals and lines indices.
        """
        boundary_vertices = []
        boundary_lines = []
        boundary_normals = []

        surface_h5_class, surface_h5_path = self._load_h5_of_gid(surface_gid)
        rm_h5_class, rm_h5_path = self._load_h5_of_gid(region_mapping_gid)

        with rm_h5_class(rm_h5_path) as rm_h5:
            array_data = rm_h5.array_data[:]

        surface_h5 = surface_h5_class(surface_h5_path)
        for slice_idx in range(surface_h5._number_of_split_slices):
            # Generate the boundaries sliced for the off case where we might overflow the buffer capacity
            slice_triangles = surface_h5.get_triangles_slice(slice_idx)
            slice_vertices = surface_h5.get_vertices_slice(slice_idx)
            slice_normals = surface_h5.get_vertex_normals_slice(slice_idx)
            first_index_in_slice = surface_h5.split_slices.load()[str(slice_idx)][KEY_VERTICES][KEY_START]
            # These will keep track of the vertices / triangles / normals for this slice that have
            # been processed and were found as a part of the boundary
            processed_vertices = []
            processed_triangles = []
            processed_normals = []
            for triangle in slice_triangles:
                triangle += first_index_in_slice
                # Check if there are two points from a triangles that are in separate regions
                # then send this to further processing that will generate the corresponding
                # region separation lines depending on the 3rd point from the triangle
                rt0, rt1, rt2 = array_data[triangle]
                if rt0 - rt1:
                    reg_idx1, reg_idx2, dangling_idx = 0, 1, 2
                elif rt1 - rt2:
                    reg_idx1, reg_idx2, dangling_idx = 1, 2, 0
                elif rt2 - rt0:
                    reg_idx1, reg_idx2, dangling_idx = 2, 0, 1
                else:
                    continue

                lines_vert, lines_ind, lines_norm = Surface._process_triangle(triangle, reg_idx1, reg_idx2,
                                                                              dangling_idx,
                                                                              first_index_in_slice, array_data,
                                                                              slice_vertices, slice_normals)
                ind_offset = len(processed_vertices) / 3
                processed_vertices.extend(lines_vert)
                processed_normals.extend(lines_norm)
                processed_triangles.extend([ind + ind_offset for ind in lines_ind])
            boundary_vertices.append(processed_vertices)
            boundary_lines.append(processed_triangles)
            boundary_normals.append(processed_normals)
        return numpy.array([boundary_vertices, boundary_lines, boundary_normals]).tolist()
