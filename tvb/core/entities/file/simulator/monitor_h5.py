from tvb.simulator.monitors import Monitor, Raw, SpatialAverage, Projection, EEG, MEG, iEEG, Bold

from tvb.core.entities.file.simulator.configurations_h5 import SimulatorConfigurationH5
from tvb.core.neotraits.h5 import Scalar, DataSet, Reference


class MonitorH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(MonitorH5, self).__init__(path, None)
        self.period = Scalar(Monitor.period, self)
        self.variables_of_interest = DataSet(Monitor.variables_of_interest, self)


class RawH5(MonitorH5):

    def __init__(self, path):
        super(RawH5, self).__init__(path)
        self.period = Scalar(Raw.period, self)
        self.variables_of_interest = DataSet(Raw.variables_of_interest, self)


class SubSampleH5(MonitorH5):
    """"""


class SpatialAverageH5(MonitorH5):

    def __init__(self, path):
        super(SpatialAverageH5, self).__init__(path)
        self.spatial_mask = DataSet(SpatialAverage.spatial_mask, self)
        self.default_mask = Scalar(SpatialAverage.default_mask, self)


class GlobalAverageH5(MonitorH5):
    """"""


class TemporalAverageH5(MonitorH5):
    """"""


class ProjectionH5(MonitorH5):

    def __init__(self, path):
        super(ProjectionH5, self).__init__(path)
        self.region_mapping = Reference(Projection.region_mapping, self)
        self.obnoise = Reference(Projection.obsnoise, self)

    def store(self, datatype, scalars_only=False, store_references=False):
        # type: (Projection) -> None
        # TODO: handle references in this case
        super(ProjectionH5, self).store(datatype, scalars_only, store_references)


class EEGH5(ProjectionH5):

    def __init__(self, path):
        super(EEGH5, self).__init__(path)
        self.projection = Reference(EEG.projection, self)
        self.sensors = Reference(EEG.sensors, self)
        self.reference = Scalar(EEG.reference, self)
        self.sigma = Scalar(EEG.sigma, self)


class MEGH5(ProjectionH5):

    def __init__(self, path):
        super(MEGH5, self).__init__(path)
        self.projection = Reference(MEG.projection, self)
        self.sensors = Reference(MEG.sensors, self)


class iEEGH5(ProjectionH5):

    def __init__(self, path):
        super(iEEGH5, self).__init__(path)
        self.projection = Reference(iEEG.projection, self)
        self.sensors = Reference(iEEG.sensors, self)
        self.sigma = Scalar(iEEG.sigma, self)


class BoldH5(MonitorH5):

    def __init__(self, path):
        super(BoldH5, self).__init__(path)
        self.period = Scalar(Bold.period, self)
        self.hrf_kernel = Reference(Bold.hrf_kernel, self)
        self.hrf_length = Scalar(Bold.hrf_length, self)

    def store(self, datatype, scalars_only=False, store_references=False):
        # type: (Bold) -> None
        super(BoldH5, self).store(datatype, scalars_only, store_references)
        hrf_kernel_gid = self.store_config_as_reference(datatype.hrf_kernel)
        self.hrf_kernel.store(hrf_kernel_gid)


class BoldRegionROIH5(BoldH5):
    """"""
