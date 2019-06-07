import numpy
from tvb.core.entities.file.datatypes.spectral_h5 import DataTypeMatrixH5
from tvb.core.neotraits.h5 import DataSet, Scalar, Reference
from tvb.datatypes.structural import StructuralMRI
from tvb.basic.arguments_serialisation import preprocess_space_parameters


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

