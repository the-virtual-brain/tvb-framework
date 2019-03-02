from tvb.core.neotraits.h5 import H5File, DataSet, Reference
from tvb.datatypes.region_mapping import RegionMapping, RegionVolumeMapping


class RegionMappingH5(H5File):

    def __init__(self, path):
        super(RegionMappingH5, self).__init__(path)
        self.array_data = DataSet(RegionMapping.array_data)
        self.connectivity = Reference(RegionMapping.connectivity)
        self.surface = Reference(RegionMapping.surface)
        self._end_accessor_declarations()


