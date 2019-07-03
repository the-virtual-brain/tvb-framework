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
.. moduleauthor:: Andrei Mihai <mihai.andrei@codemart.ro>

"""

import os
import json
import numpy
from tvb.basic.filters.chain import FilterChain
from tvb.basic.arguments_serialisation import parse_slice, slice_str
from tvb.core.adapters.abcadapter import ABCAdapterForm
from tvb.core.adapters.abcdisplayer import ABCDisplayer
from tvb.core.entities.model.datatypes.spectral import DataTypeMatrix
from tvb.core.neotraits._forms import DataTypeSelectField, SimpleStrField
from tvb.interfaces.neocom.h5 import DirLoader
from tvb.interfaces.neocom.config import registry


# TODO: rewrite, necessary to read whole matrix?
def compute_2d_view(matrix, slice_s):
    """
    Create a 2d view of the matrix using the suggested slice
    If the given slice is invalid or fails to produce a 2d array the default is used
    which selects the first 2 dimensions.
    If the matrix is complex the real part is shown
    :param slice_s: a string representation of a slice
    :return: (a 2d array,  the slice used to make it, is_default_returned)
    """
    default = (slice(None), slice(None)) + tuple(0 for _ in range(matrix.ndim - 2))  # [:,:,0,0,0,0 etc]

    try:
        if slice_s is not None:
            matrix_slice = parse_slice(slice_s)
        else:
            matrix_slice = slice(None)

        m = matrix[matrix_slice]

        if m.ndim > 2:  # the slice did not produce a 2d array, treat as error
            raise ValueError(str(matrix.shape))

    except (IndexError, ValueError):  # if the slice could not be parsed or it failed to produce a 2d array
        matrix_slice = default

    slice_used = slice_str(matrix_slice)
    return matrix[matrix_slice].astype(float), slice_used, matrix_slice == default


class MappedArraySVGVisualizerMixin(object):
    """
    To be mixed in a ABCDisplayer
    """

    def get_required_memory_size(self, datatype):
        input_size = datatype.read_data_shape()
        return numpy.prod(input_size) / input_size[0] * 8.0

    def generate_preview(self, datatype, **kwargs):
        result = self.launch(datatype)
        result["isPreview"] = True
        return result

    @staticmethod
    def compute_raw_matrix_params(matrix):
        """
        Serializes matrix data, shape and stride metadata to json
        """
        matrix_data = ABCDisplayer.dump_with_precision(matrix.flat)
        matrix_shape = json.dumps(matrix.shape)

        return dict(matrix_data=matrix_data,
                    matrix_shape=matrix_shape)

    def compute_params(self, matrix, viewer_title, given_slice=None, labels=None):
        """
        Prepare a 2d matrix to display
        :param matrix: input matrix
        :param given_slice: a string representation of a slice. This slice should cut a 2d view from matrix
        If the matrix is not 2d and the slice will not make it 2d then a default slice is used
        """
        matrix2d, slice_used, is_default_slice = compute_2d_view(matrix, given_slice)

        view_pars = self.compute_raw_matrix_params(matrix2d)
        view_pars.update(original_matrix_shape=str(matrix.shape),
                         show_slice_info=given_slice is not None,
                         given_slice=given_slice,
                         slice_used=slice_used,
                         is_default_slice=is_default_slice,
                         viewer_title=viewer_title,
                         title=viewer_title,
                         matrix_labels=json.dumps(labels))
        return view_pars

    def _extract_labels_and_data_matrix(self, datatype_index):
        """
        If datatype has a source attribute of type TimeSeriesRegion
        then the labels of the associated connectivity are returned.
        Else None
        """
        h5_class = registry.get_h5file_for_index(type(datatype_index))
        dir_loader = DirLoader(os.path.join(os.path.dirname(self.storage_path),
                                            str(datatype_index.fk_from_operation)))
        h5_path = dir_loader.path_for(h5_class, datatype_index.gid)
        with h5_class(h5_path) as datatype_h5:
            source_gid = datatype_h5.source.load()
            matrix = datatype_h5.array_data[:]

        source_h5_class, source_h5_path = self._load_h5_of_gid(source_gid.hex)
        with source_h5_class(source_h5_path) as source_h5:
            # todo should we use connectivity.ordered_labels?
            # If so also permute the matrix to be consistent with the conn views
            labels = self.get_space_labels(source_h5)

        return [labels, labels], matrix


class MatrixVisualizerForm(ABCAdapterForm):

    def __init__(self, prefix='', project_id=None):
        super(MatrixVisualizerForm, self).__init__(prefix, project_id, False)
        self.datatype = DataTypeSelectField(self.get_required_datatype(), self, name='datatype', required=True,
                                            label='Array data type', conditions=self.get_filters())
        self.slice = SimpleStrField(self, name='slice', label='slice indices in numpy syntax')

    @staticmethod
    def get_input_name():
        return '_datatype'

    @staticmethod
    def get_filters():
        return FilterChain(fields=[FilterChain.datatype + '.ndim'], operations=[">="], values=[2])

    @staticmethod
    def get_required_datatype():
        return DataTypeMatrix


class MappedArrayVisualizer(MappedArraySVGVisualizerMixin, ABCDisplayer):
    _ui_name = "Matrix Visualizer"
    _ui_subsection = "matrix"
    form = None

    def get_input_tree(self): return None

    def get_form(self):
        if self.form is None:
            return MatrixVisualizerForm
        return self.form

    def set_form(self, form):
        self.form = form

    def launch(self, datatype, slice=''):
        loader = DirLoader(os.path.join(os.path.dirname(self.storage_path), str(datatype.fk_from_operation)))
        h5_class = registry.get_h5file_for_index(type(datatype))
        h5_path = loader.path_for(h5_class, datatype.gid)
        with h5_class(h5_path) as h5_file:
            matrix = h5_file.array_data.load()

        matrix2d, _, _ = compute_2d_view(matrix, slice)
        title = datatype.display_name + " matrix plot"

        pars = self.compute_params(matrix, title, slice)
        return self.build_display_result("matrix/svg_view", pars)
