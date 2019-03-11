import numpy
from tvb.core.entities.file.datatypes.structural_h5 import VolumetricDataMixin
from tvb.core.neotraits.h5 import H5File, DataSet, Reference
from tvb.datatypes.region_mapping import RegionMapping, RegionVolumeMapping
from tvb.basic.arguments_serialisation import preprocess_time_parameters, preprocess_space_parameters, postprocess_voxel_ts, parse_slice

from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)



class RegionMappingH5(H5File):

    def __init__(self, path):
        super(RegionMappingH5, self).__init__(path)
        self.array_data = DataSet(RegionMapping.array_data, self)
        self.connectivity = Reference(RegionMapping.connectivity, self)
        self.surface = Reference(RegionMapping.surface, self)



class RegionVolumeMappingH5(VolumetricDataMixin, H5File):

    def __init__(self, path):
        super(RegionVolumeMappingH5, self).__init__(path)
        self.array_data = DataSet(RegionVolumeMapping.array_data, self)
        self.connectivity = Reference(RegionVolumeMapping.connectivity, self)
        self.volume = Reference(RegionVolumeMapping.volume, self)

    # fixme: these are broken!
    def write_data_slice(self, data):
        """
        We are using here the same signature as in TS, just to allow easier parsing code.
        This method will also validate the data range nd convert it to int, along with writing it is H5.

        :param data: 3D int array
        """

        LOG.info("Writing RegionVolumeMapping with min=%d, mix=%d" % (data.min(), data.max()))
        if self.apply_corrections:
            data = numpy.array(data, dtype=numpy.int32)
            data[data >= self.connectivity.number_of_regions] = -1
            data[data < -1] = -1
            LOG.debug("After corrections: RegionVolumeMapping min=%d, mix=%d" % (data.min(), data.max()))

        if self.mappings_file:
            try:
                mapping_data = numpy.loadtxt(self.mappings_file, dtype=numpy.str, usecols=(0, 2))
                mapping_data = {int(row[0]): int(row[1]) for row in mapping_data}
            except Exception:
                raise exceptions.ValidationException("Invalid Mapping File. Expected 3 columns (int, string, int)")

            if len(data.shape) != 3:
                raise exceptions.ValidationException('Invalid RVM data. Expected 3D.')

            not_matched = set()
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    for k in range(data.shape[2]):
                        val = data[i][j][k]
                        if not mapping_data.has_key(val):
                            not_matched.add(val)
                        data[i][j][k] = mapping_data.get(val, -1)

            LOG.info("Imported RM with values in interval [%d - %d]" % (data.min(), data.max()))
            if not_matched:
                LOG.warn("Not matched regions will be considered background: %s" % not_matched)

        if data.min() < -1 or data.max() >= self.connectivity.number_of_regions:
            raise exceptions.ValidationException("Invalid Mapping array: [%d ... %d]" % (data.min(), data.max()))

        self.store_data("array_data", data)


    def get_voxel_region(self, x_plane, y_plane, z_plane):
        x_plane, y_plane, z_plane = preprocess_space_parameters(x_plane, y_plane, z_plane, self.length_1d,
                                                                self.length_2d, self.length_3d)
        slices = slice(x_plane, x_plane + 1), slice(y_plane, y_plane + 1), slice(z_plane, z_plane + 1)
        voxel = self.read_data_slice(slices)[0, 0, 0]
        if voxel != -1:
            return self.connectivity.region_labels[int(voxel)]
        else:
            return 'background'


    def get_mapped_array_volume_view(self, mapped_array, x_plane, y_plane, z_plane, mapped_array_slice=None, **kwargs):
        x_plane, y_plane, z_plane = preprocess_space_parameters(x_plane, y_plane, z_plane, self.length_1d,
                                                                self.length_2d, self.length_3d)
        slice_x, slice_y, slice_z = self.get_volume_slice(x_plane, y_plane, z_plane)

        if mapped_array_slice:
            matrix_slice = parse_slice(mapped_array_slice)
            measure = mapped_array.get_data('array_data', matrix_slice)
        else:
            measure = mapped_array.get_data('array_data')

        if measure.shape != (self.connectivity.number_of_regions, ):
            raise ValueError('cannot project measure on the space')

        result_x = measure[slice_x]
        result_y = measure[slice_y]
        result_z = measure[slice_z]
        # Voxels outside the brain are -1. The indexing above is incorrect for those voxels as it
        # associates the values of the last region measure[-1] to them.
        # Here we replace those values with an out of scale value.
        result_x[slice_x==-1] = measure.min() - 1
        result_y[slice_y==-1] = measure.min() - 1
        result_z[slice_z==-1] = measure.min() - 1

        return [[result_x.tolist()],
                [result_y.tolist()],
                [result_z.tolist()]]

