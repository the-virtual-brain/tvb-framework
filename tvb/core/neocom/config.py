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

from tvb.datatypes.connectivity import Connectivity
from tvb.datatypes.fcd import Fcd
from tvb.datatypes.graph import ConnectivityMeasure, CorrelationCoefficients, Covariance
from tvb.datatypes.local_connectivity import LocalConnectivity
from tvb.datatypes.mode_decompositions import PrincipalComponents, IndependentComponents
from tvb.datatypes.patterns import StimuliRegion, StimuliSurface
from tvb.datatypes.projections import ProjectionMatrix
from tvb.datatypes.region_mapping import RegionVolumeMapping, RegionMapping
from tvb.datatypes.sensors import Sensors
from tvb.datatypes.simulation_state import SimulationState
from tvb.datatypes.spectral import CoherenceSpectrum, ComplexCoherenceSpectrum, FourierSpectrum, WaveletCoefficients
from tvb.datatypes.structural import StructuralMRI
from tvb.datatypes.surfaces import Surface
from tvb.datatypes.temporal_correlations import CrossCorrelation
from tvb.datatypes.time_series import TimeSeries, TimeSeriesRegion, TimeSeriesSurface, TimeSeriesVolume
from tvb.datatypes.time_series import TimeSeriesEEG, TimeSeriesMEG, TimeSeriesSEEG
from tvb.datatypes.tracts import Tracts
from tvb.datatypes.volumes import Volume
from tvb.core.entities.file.datatypes.annotation_h5 import ConnectivityAnnotationsH5
from tvb.core.entities.file.datatypes.connectivity_h5 import ConnectivityH5
from tvb.core.entities.file.datatypes.fcd_h5 import FcdH5
from tvb.core.entities.file.datatypes.graph_h5 import ConnectivityMeasureH5, CorrelationCoefficientsH5, CovarianceH5
from tvb.core.entities.file.datatypes.local_connectivity_h5 import LocalConnectivityH5
from tvb.core.entities.file.datatypes.mode_decompositions_h5 import PrincipalComponentsH5, IndependentComponentsH5
from tvb.core.entities.file.datatypes.patterns_h5 import StimuliRegionH5, StimuliSurfaceH5
from tvb.core.entities.file.datatypes.projections_h5 import ProjectionMatrixH5
from tvb.core.entities.file.datatypes.region_mapping_h5 import RegionMappingH5, RegionVolumeMappingH5
from tvb.core.entities.file.datatypes.sensors_h5 import SensorsH5
from tvb.core.entities.file.datatypes.simulation_state_h5 import SimulationStateH5
from tvb.core.entities.file.datatypes.spectral_h5 import CoherenceSpectrumH5, ComplexCoherenceSpectrumH5
from tvb.core.entities.file.datatypes.spectral_h5 import FourierSpectrumH5, WaveletCoefficientsH5
from tvb.core.entities.file.datatypes.structural_h5 import StructuralMRIH5
from tvb.core.entities.file.datatypes.surface_h5 import SurfaceH5
from tvb.core.entities.file.datatypes.temporal_correlations_h5 import CrossCorrelationH5
from tvb.core.entities.file.datatypes.time_series import TimeSeriesH5, TimeSeriesRegionH5, TimeSeriesSurfaceH5, \
    TimeSeriesVolumeH5, TimeSeriesEEGH5, TimeSeriesMEGH5, TimeSeriesSEEGH5
from tvb.core.entities.file.datatypes.tracts_h5 import TractsH5
from tvb.core.entities.file.datatypes.volumes_h5 import VolumeH5
from tvb.core.entities.model.datatypes.annotation import ConnectivityAnnotationsIndex
from tvb.core.entities.model.datatypes.connectivity import ConnectivityIndex
from tvb.core.entities.model.datatypes.fcd import FcdIndex
from tvb.core.entities.model.datatypes.graph import ConnectivityMeasureIndex, CorrelationCoefficientsIndex, \
    CovarianceIndex
from tvb.core.entities.model.datatypes.local_connectivity import LocalConnectivityIndex
from tvb.core.entities.model.datatypes.mode_decompositions import PrincipalComponentsIndex, IndependentComponentsIndex
from tvb.core.entities.model.datatypes.patterns import StimuliRegionIndex, StimuliSurfaceIndex
from tvb.core.entities.model.datatypes.projections import ProjectionMatrixIndex
from tvb.core.entities.model.datatypes.region_mapping import RegionVolumeMappingIndex, RegionMappingIndex
from tvb.core.entities.model.datatypes.sensors import SensorsIndex
from tvb.core.entities.model.datatypes.spectral import CoherenceSpectrumIndex, ComplexCoherenceSpectrumIndex, \
    FourierSpectrumIndex, WaveletCoefficientsIndex
from tvb.core.entities.model.datatypes.structural import StructuralMRIIndex
from tvb.core.entities.model.datatypes.surface import SurfaceIndex
from tvb.core.entities.model.datatypes.temporal_correlations import CrossCorrelationIndex
from tvb.core.entities.model.datatypes.time_series import TimeSeriesIndex, TimeSeriesRegionIndex, \
    TimeSeriesSurfaceIndex, TimeSeriesVolumeIndex, TimeSeriesEEGIndex, TimeSeriesMEGIndex, TimeSeriesSEEGIndex
from tvb.core.entities.model.datatypes.tracts import TractsIndex
from tvb.core.entities.model.datatypes.volume import VolumeIndex
from tvb.core.neocom._registry import Registry

# an alternative approach is to make each h5file declare if it has a corresponding datatype
# then in a metaclass hook each class creation and populate a map
registry = Registry()
registry.register_h5file_datatype(ConnectivityH5, Connectivity, ConnectivityIndex)
registry.register_h5file_datatype(ConnectivityAnnotationsH5, None, ConnectivityAnnotationsIndex)
registry.register_h5file_datatype(LocalConnectivityH5, LocalConnectivity, LocalConnectivityIndex)
registry.register_h5file_datatype(ProjectionMatrixH5, ProjectionMatrix, ProjectionMatrixIndex)
registry.register_h5file_datatype(RegionVolumeMappingH5, RegionVolumeMapping, RegionVolumeMappingIndex)
registry.register_h5file_datatype(RegionMappingH5, RegionMapping, RegionMappingIndex)
registry.register_h5file_datatype(SensorsH5, Sensors, SensorsIndex)
registry.register_h5file_datatype(SimulationStateH5, SimulationState, None)
registry.register_h5file_datatype(CoherenceSpectrumH5, CoherenceSpectrum, CoherenceSpectrumIndex)
registry.register_h5file_datatype(ComplexCoherenceSpectrumH5, ComplexCoherenceSpectrum, ComplexCoherenceSpectrumIndex)
registry.register_h5file_datatype(FourierSpectrumH5, FourierSpectrum, FourierSpectrumIndex)
registry.register_h5file_datatype(WaveletCoefficientsH5, WaveletCoefficients, WaveletCoefficientsIndex)
registry.register_h5file_datatype(StructuralMRIH5, StructuralMRI, StructuralMRIIndex)
registry.register_h5file_datatype(SurfaceH5, Surface, SurfaceIndex)
registry.register_h5file_datatype(CrossCorrelationH5, CrossCorrelation, CrossCorrelationIndex)
registry.register_h5file_datatype(TimeSeriesH5, TimeSeries, TimeSeriesIndex)
registry.register_h5file_datatype(TimeSeriesRegionH5, TimeSeriesRegion, TimeSeriesRegionIndex)
registry.register_h5file_datatype(TimeSeriesSurfaceH5, TimeSeriesSurface, TimeSeriesSurfaceIndex)
registry.register_h5file_datatype(TimeSeriesVolumeH5, TimeSeriesVolume, TimeSeriesVolumeIndex)
registry.register_h5file_datatype(TimeSeriesEEGH5, TimeSeriesEEG, TimeSeriesEEGIndex)
registry.register_h5file_datatype(TimeSeriesMEGH5, TimeSeriesMEG, TimeSeriesMEGIndex)
registry.register_h5file_datatype(TimeSeriesSEEGH5, TimeSeriesSEEG, TimeSeriesSEEGIndex)
registry.register_h5file_datatype(TractsH5, Tracts, TractsIndex)
registry.register_h5file_datatype(VolumeH5, Volume, VolumeIndex)
registry.register_h5file_datatype(PrincipalComponentsH5, PrincipalComponents, PrincipalComponentsIndex)
registry.register_h5file_datatype(IndependentComponentsH5, IndependentComponents, IndependentComponentsIndex)
registry.register_h5file_datatype(ConnectivityMeasureH5, ConnectivityMeasure, ConnectivityMeasureIndex)
registry.register_h5file_datatype(CorrelationCoefficientsH5, CorrelationCoefficients, CorrelationCoefficientsIndex)
registry.register_h5file_datatype(CovarianceH5, Covariance, CovarianceIndex)
registry.register_h5file_datatype(FcdH5, Fcd, FcdIndex)
registry.register_h5file_datatype(StimuliRegionH5, StimuliRegion, StimuliRegionIndex)
registry.register_h5file_datatype(StimuliSurfaceH5, StimuliSurface, StimuliSurfaceIndex)
