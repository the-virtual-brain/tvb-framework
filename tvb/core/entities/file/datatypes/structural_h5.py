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
import numpy
from tvb.core.adapters.arguments_serialisation import preprocess_space_parameters
from tvb.core.entities.file.datatypes.spectral_h5 import DataTypeMatrixH5
from tvb.core.neotraits.h5 import DataSet, Scalar, Reference
from tvb.datatypes.structural import StructuralMRI


class VolumetricDataMixin(object):
    """Provides subclasses with useful methods for volumes."""

    array_data = None  # type: DataSet  # here only for typing, will be overriden in mixed in class

    def write_data_slice(self, data):
        """
        We are using here the same signature as in TS, just to allow easier parsing code.
        This is not a chunked write.

        """
        self.array_data.store(data)

    def get_volume_slice(self, x_plane, y_plane, z_plane):
        shape = self.array_data.shape
        length_1d = shape[0]
        length_2d = shape[1]
        length_3d = shape[2]

        slices = slice(length_1d), slice(length_2d), slice(z_plane, z_plane + 1)
        slice_x = self.array_data[slices][:, :, 0]  # 2D
        slice_x = numpy.array(slice_x, dtype=int)

        slices = slice(x_plane, x_plane + 1), slice(length_2d), slice(length_3d)
        slice_y = self.array_data[slices][0, :, :][..., ::-1]
        slice_y = numpy.array(slice_y, dtype=int)

        slices = slice(length_1d), slice(y_plane, y_plane + 1), slice(length_3d)
        slice_z = self.array_data[slices][:, 0, :][..., ::-1]
        slice_z = numpy.array(slice_z, dtype=int)

        return [slice_x, slice_y, slice_z]

    def get_volume_view(self, x_plane, y_plane, z_plane, **kwargs):
        shape = self.array_data.shape
        length_1d = shape[0]
        length_2d = shape[1]
        length_3d = shape[2]
        # Work with space inside Volume:
        x_plane, y_plane, z_plane = preprocess_space_parameters(x_plane, y_plane, z_plane, length_1d,
                                                                length_2d, length_3d)
        slice_x, slice_y, slice_z = self.get_volume_slice(x_plane, y_plane, z_plane)
        return [[slice_x.tolist()], [slice_y.tolist()], [slice_z.tolist()]]


class StructuralMRIH5(VolumetricDataMixin, DataTypeMatrixH5):

    def __init__(self, path):
        super(StructuralMRIH5, self).__init__(path)
        self.array_data = DataSet(StructuralMRI.array_data, self)
        self.weighting = Scalar(StructuralMRI.weighting, self)
        self.volume = Reference(StructuralMRI.volume, self)
