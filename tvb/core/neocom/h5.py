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

# flatten the import paths for simpler usage
from tvb.core.entities.file.datatypes.connectivity_h5 import ConnectivityH5
from tvb.core.entities.file.datatypes.local_connectivity_h5 import LocalConnectivityH5
from tvb.core.entities.file.datatypes.projections_h5 import ProjectionMatrixH5
from tvb.core.entities.file.datatypes.region_mapping_h5 import RegionMappingH5, RegionVolumeMappingH5
from tvb.core.entities.file.datatypes.sensors_h5 import SensorsH5
from tvb.core.entities.file.datatypes.simulation_state_h5 import SimulationStateH5
from tvb.core.entities.file.datatypes.spectral_h5 import (
    CoherenceSpectrumH5, ComplexCoherenceSpectrumH5,
    FourierSpectrumH5, WaveletCoefficientsH5
)
from tvb.core.entities.file.datatypes.structural_h5 import StructuralMRIH5
from tvb.core.entities.file.datatypes.surface_h5 import SurfaceH5
from tvb.core.entities.file.datatypes.temporal_correlations_h5 import CrossCorrelationH5
from tvb.core.entities.file.datatypes.time_series import (
    TimeSeriesH5, TimeSeriesRegionH5,
    TimeSeriesSurfaceH5, TimeSeriesVolumeH5
)
from tvb.core.entities.file.datatypes.tracts_h5 import TractsH5
from tvb.core.entities.file.datatypes.volumes_h5 import VolumeH5
from tvb.core.neocom._h5loader import Loader, DirLoader

import typing

if typing.TYPE_CHECKING:
    from tvb.basic.neotraits.api import HasTraits
    import uuid


def load(source):
    # type: (str) -> HasTraits
    """
    Load a datatype stored in the tvb h5 file found at the given path
    """
    loader = Loader()
    return loader.load(source)


def store(datatype, destination):
    # type: (HasTraits, str) -> None
    """
    Stores the given datatype in a tvb h5 file at the given path
    """
    loader = Loader()
    return loader.store(datatype, destination)


def load_from_dir(base_dir, gid, recursive=False):
    # type: (str, typing.Union[str, uuid.UUID], bool) -> HasTraits
    """
    Loads a datatype with the requested gid from the given directory.
    The datatype should have been written with store_to_dir
    The name and location of the file is chosen for you.
    :param base_dir:  The h5 storage directory
    :param gid: the gid of the to be loaded datatype
    :param recursive: if datatypes contained in this datatype should be loaded as well
    """
    loader = DirLoader(base_dir, recursive)
    return loader.load(gid)


def store_to_dir(base_dir, datatype, recursive=False):
    # type: (str, HasTraits, bool) -> None
    """
    Stores the given datatype in the given directory.
    The name and location of the stored file(s) is chosen for you by this function.
    If recursive is true than datatypes referenced by this one are stored as well.
    """
    loader = DirLoader(base_dir, recursive)
    loader.store(datatype)

