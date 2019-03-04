from tvb.datatypes.fcd import Fcd

from tvb.core.neotraits.h5 import H5File, DataSet, Reference, Scalar, Json


class FcdH5(H5File):

    def __init__(self, path):
        super(FcdH5, self).__init__(path)
        self.array_data = DataSet(Fcd.array_data, self)
        self.source = Reference(Fcd.source, self)
        self.sw = Scalar(Fcd.sw, self)
        self.sp = Scalar(Fcd.sp, self)
        self.labels_ordering = Json(Fcd.labels_ordering, self)
