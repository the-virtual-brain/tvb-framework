import numpy
from tvb.basic.exceptions import ValidationException
from tvb.core.entities.file.datatypes.spectral_h5 import DataTypeMatrixH5
from tvb.core.entities.file.datatypes.structural_h5 import VolumetricDataMixin
from tvb.core.entities.load import load_entity_by_gid
from tvb.core.neotraits.h5 import H5File, DataSet, Reference
from tvb.datatypes.region_mapping import RegionMapping, RegionVolumeMapping
from tvb.basic.arguments_serialisation import preprocess_space_parameters

from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)



class RegionMappingH5(H5File):

    def __init__(self, path):
        super(RegionMappingH5, self).__init__(path)
        self.array_data = DataSet(RegionMapping.array_data, self)
        self.connectivity = Reference(RegionMapping.connectivity, self)
        self.surface = Reference(RegionMapping.surface, self)



class RegionVolumeMappingH5(VolumetricDataMixin, DataTypeMatrixH5):

    def __init__(self, path):
        super(RegionVolumeMappingH5, self).__init__(path)
        self.array_data = DataSet(RegionVolumeMapping.array_data, self)
        self.connectivity = Reference(RegionVolumeMapping.connectivity, self)
        self.volume = Reference(RegionVolumeMapping.volume, self)

    # fixme: these are broken!
    def write_data_slice(self, data, apply_corrections=False, mappings_file=None, conn_nr_regions=76):
        """
        We are using here the same signature as in TS, just to allow easier parsing code.
        This method will also validate the data range nd convert it to int, along with writing it is H5.

        :param data: 3D int array
        """

        LOG.info("Writing RegionVolumeMapping with min=%d, mix=%d" % (data.min(), data.max()))
        if apply_corrections:
            data = numpy.array(data, dtype=numpy.int32)
            data[data >= conn_nr_regions] = -1
            data[data < -1] = -1
            LOG.debug("After corrections: RegionVolumeMapping min=%d, mix=%d" % (data.min(), data.max()))

        if mappings_file:
            try:
                mapping_data = numpy.loadtxt(mappings_file, dtype=numpy.str, usecols=(0, 2))
                mapping_data = {int(row[0]): int(row[1]) for row in mapping_data}
            except Exception:
                raise ValidationException("Invalid Mapping File. Expected 3 columns (int, string, int)")

            if len(data.shape) != 3:
                raise ValidationException('Invalid RVM data. Expected 3D.')

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

        if data.min() < -1 or data.max() >= conn_nr_regions:
            raise ValidationException("Invalid Mapping array: [%d ... %d]" % (data.min(), data.max()))

        self.array_data.store(data)


    def get_voxel_region(self, x_plane, y_plane, z_plane):
        data_shape = self.array_data.shape
        x_plane, y_plane, z_plane = preprocess_space_parameters(x_plane, y_plane, z_plane, data_shape[0],
                                                                data_shape[1], data_shape[2])
        slices = slice(x_plane, x_plane + 1), slice(y_plane, y_plane + 1), slice(z_plane, z_plane + 1)
        voxel = self.array_data[slices][0, 0, 0]
        if voxel != -1:
            conn_index = load_entity_by_gid(self.connectivity.load().hex)
            return conn_index.region_labels[int(voxel)]
        else:
            return 'background'
