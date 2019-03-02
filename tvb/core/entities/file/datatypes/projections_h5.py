from tvb.core.neotraits.h5 import H5File, DataSet, Scalar, Reference, Json

from tvb.datatypes.projections import ProjectionMatrix


class ProjectionMatrixH5(H5File):

    def __init__(self, path):
        super(ProjectionMatrixH5, self).__init__(path)
        self.projection_type = Scalar(ProjectionMatrix.projection_type)
        self.brain_skull = Reference(ProjectionMatrix.brain_skull)
        self.skull_skin = Reference(ProjectionMatrix.skull_skin)
        self.skin_air = Reference(ProjectionMatrix.skin_air)
        self.conductances = Json(ProjectionMatrix.conductances)
        self.sources = Reference(ProjectionMatrix.sources)
        self.sensors = Reference(ProjectionMatrix.sensors)
        self.projection_data = DataSet(ProjectionMatrix.projection_data)
        self._end_accessor_declarations()
