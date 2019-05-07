import scipy.sparse
from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from tvb.datatypes.local_connectivity import LocalConnectivity

from tvb.core.entities.model.datatypes.surface import SurfaceIndex
from tvb.core.neotraits.db import HasTraitsIndex, from_ndarray


class LocalConnectivityIndex(HasTraitsIndex):
    id = Column(Integer, ForeignKey(HasTraitsIndex.id), primary_key=True)

    surface_id = Column(Integer, ForeignKey(SurfaceIndex.id), nullable=not LocalConnectivity.surface.required)
    surface = relationship(SurfaceIndex, foreign_keys=surface_id, primaryjoin=SurfaceIndex.id == surface_id)


    matrix_non_zero_min = Column(Float)
    matrix_non_zero_max = Column(Float)
    matrix_non_zero_mean = Column(Float)

    def fill_from_has_traits(self, datatype):
        self.gid = datatype.gid.hex
        I, J, V = scipy.sparse.find(datatype.matrx)
        self.matrix_non_zero_min, self.matrix_non_zero_max, self.matrix_non_zero_mean = from_ndarray(V)
