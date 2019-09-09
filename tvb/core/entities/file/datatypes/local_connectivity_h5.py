from tvb.basic.neotraits.api import Attr
from tvb.core.neotraits.h5 import H5File, DataSet, Scalar, Reference, SparseMatrix, Json
from tvb.datatypes.equations import Equation
from tvb.datatypes.local_connectivity import LocalConnectivity


class LocalConnectivityH5(H5File):
    def __init__(self, path, generic_attributes=None):
        super(LocalConnectivityH5, self).__init__(path, generic_attributes)
        self.surface = Reference(LocalConnectivity.surface, self)
        # this multidataset accessor works but something is off about it
        # this would be clearer
        # self.matrix, self.matrixindices, self.matrixindptr
        self.matrix = SparseMatrix(LocalConnectivity.matrix, self)
        # equation is an inlined reference
        # should this be a special equation scalar field?
        # or this?
        # this is clear about the structure, but obviously breaks the default store/load
        # self.equation_equation = Scalar(Equation.equation, self)
        # self.equation_parameters = Scalar(Equation.parameters, self)

        self.equation = Scalar(Attr(str), self, name='equation')
        self.cutoff = Scalar(LocalConnectivity.cutoff, self)

    # equations are such a special case that we will have to implement custom load store

    def store(self, datatype, scalars_only=False):
        self.surface.store(datatype.surface)
        self.matrix.store(datatype.matrix)
        self.cutoff.store(datatype.cutoff)
        self.equation.store(datatype.equation.to_json(datatype.equation))

    def load_into(self, datatype):
        datatype.matrix = self.matrix.load()
        datatype.cutoff = self.cutoff.load()
        eq = self.equation.load()
        eq = datatype.equation.from_json(eq)
        datatype.equation = eq

    def get_min_max_values(self):
        metadata = self.matrix.get_metadata()
        return metadata.min, metadata.max

