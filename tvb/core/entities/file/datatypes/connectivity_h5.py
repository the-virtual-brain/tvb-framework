from tvb.core.neotraits.h5 import H5File, DataSet, Scalar
from tvb.datatypes.connectivity import Connectivity


class ConnectivityH5(H5File):
    def __init__(self, path):
        super(ConnectivityH5, self).__init__(path)
        self.region_labels = DataSet(Connectivity.region_labels)
        self.weights = DataSet(Connectivity.weights)
        self.undirected = Scalar(Connectivity.undirected)
        self.tract_lengths = DataSet(Connectivity.tract_lengths)
        self.centres = DataSet(Connectivity.centres)
        self.cortical = DataSet(Connectivity.cortical)
        self.hemispheres = DataSet(Connectivity.hemispheres)
        self.orientations = DataSet(Connectivity.orientations)
        self.areas = DataSet(Connectivity.areas)
        self.number_of_regions = Scalar(Connectivity.number_of_regions)
        self.number_of_connections = Scalar(Connectivity.number_of_connections)
        self.parent_connectivity = Scalar(Connectivity.parent_connectivity)
        self._end_accessor_declarations()
