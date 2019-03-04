# flatten the import paths for simpler usage
from tvb.core.entities.file.datatypes.connectivity_h5 import ConnectivityH5
from tvb.core.entities.file.datatypes.local_connectivity_h5 import LocalConnectivityH5
from tvb.core.entities.file.datatypes.projections_h5 import ProjectionMatrixH5
from tvb.core.entities.file.datatypes.region_mapping_h5 import RegionMappingH5, RegionVolumeMappingH5
from tvb.core.entities.file.datatypes.sensors_h5 import SensorsH5
from tvb.core.entities.file.datatypes.simulation_state_h5 import SimulationStateH5
from tvb.core.entities.file.datatypes.spectral_h5 import CoherenceSpectrumH5, ComplexCoherenceSpectrumH5, FourierSpectrumH5, WaveletCoefficientsH5
from tvb.core.entities.file.datatypes.structural_h5 import StructuralMRIH5
from tvb.core.entities.file.datatypes.surface_h5 import SurfaceH5
from tvb.core.entities.file.datatypes.temporal_correlations_h5 import CrossCorrelationH5
from tvb.core.entities.file.datatypes.time_series import TimeSeriesH5, TimeSeriesRegionH5, TimeSeriesSurfaceH5, TimeSeriesVolumeH5
from tvb.core.entities.file.datatypes.tracts_h5 import TractsH5
from tvb.core.entities.file.datatypes.volumes_h5 import VolumeH5
from tvb.interfaces.neocom import _h5impl
from tvb.interfaces.neocom._h5loader import Loader, DirLoader


_registry = _h5impl.build_registry()


def load(source):
    loader = Loader(_registry)
    return loader.load(source)


def store(datatype, destination):
    loader = Loader(_registry)
    return loader.store(datatype, destination)


def load_from_dir(base_dir, gid, recursive=False):
    loader = DirLoader(base_dir, _registry, recursive)
    return loader.load(gid)


def store_to_dir(base_dir, datatype, recursive=False):
    loader = DirLoader(base_dir, _registry, recursive)
    loader.store(datatype)

