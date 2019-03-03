import json
import numpy
import scipy.sparse

from ._h5core import DataSetMetaData, Accessor, Scalar


class SparseMatrixMetaData(DataSetMetaData):
    """
    Essential metadata for interpreting a sparse matrix stored in h5
    """
    def __init__(self, minimum, maximum, format, dtype, shape):
        super(SparseMatrixMetaData, self).__init__(minimum, maximum)
        self.dtype = dtype
        self.format = format
        self.shape = shape

    @staticmethod
    def parse_shape(shapestr):
        if not shapestr or shapestr[0] != '(' or shapestr[-1] != ')':
            raise ValueError('can not parse shape "{}"'.format(shapestr))
        frags = shapestr[1:-1].split(',')
        return tuple(long(e) for e in frags)

    @classmethod
    def from_array(cls, mtx):
        return cls(
            minimum=mtx.data.min(),
            maximum=mtx.data.max(),
            format=mtx.format,
            dtype=mtx.dtype,
            shape=mtx.shape,
        )

    @classmethod
    def from_dict(cls, dikt):
        return cls(
            minimum=dikt['Minimum'],
            maximum=dikt['Maximum'],
            format=dikt['format'],
            dtype=numpy.dtype(dikt['dtype']),
            shape=cls.parse_shape(dikt['Shape']),
        )

    def to_dict(self):
        return {
            'Minimum': self.min,
            'Maximum': self.max,
            'format': self.format,
            'dtype': self.dtype.str,
            'Shape': str(self.shape),
        }



class SparseMatrix(Accessor):
    """
    Stores and loads a scipy.sparse csc or csr matrix in h5.
    """
    constructors = {'csr': scipy.sparse.csr_matrix, 'csc': scipy.sparse.csc_matrix}

    def store(self, mtx):
        # type: (scipy.sparse.spmatrix) -> None
        # noinspection PyProtectedMember
        mtx = self.trait_attribute._validate_set(None, mtx)
        if mtx is None:
            return
        if mtx.format not in self.constructors:
            raise ValueError('sparse format {} not supported'.format(mtx.format))

        if not isinstance(mtx, scipy.sparse.spmatrix):
            raise TypeError("expected scipy.sparse.spmatrix, got {}".format(type(mtx)))

        self.owner.storage_manager.store_data(
            'data',
            mtx.data,
            where=self.field_name
        )
        self.owner.storage_manager.store_data(
            'indptr',
            mtx.indptr,
            where=self.field_name
        )
        self.owner.storage_manager.store_data(
            'indices',
            mtx.indices,
            where=self.field_name
        )
        self.owner.storage_manager.set_metadata(
            SparseMatrixMetaData.from_array(mtx).to_dict(),
            where=self.field_name
        )

    def get_metadata(self):
        meta = self.owner.storage_manager.get_metadata(self.field_name)
        return SparseMatrixMetaData.from_dict(meta)

    def load(self):
        meta = self.get_metadata()
        if meta.format not in self.constructors:
            raise ValueError('sparse format {} not supported'.format(meta.format))
        constructor = self.constructors[meta.format]
        data = self.owner.storage_manager.get_data(
            'data',
            where=self.field_name,
        )
        indptr = self.owner.storage_manager.get_data(
            'indptr',
            where=self.field_name,
        )
        indices = self.owner.storage_manager.get_data(
            'indices',
            where=self.field_name,
        )
        mtx = constructor((data, indices, indptr), shape=meta.shape, dtype=meta.dtype)
        mtx.sort_indices()
        return mtx



class Json(Scalar):
    """
    A python json like data structure accessor
    This works with simple Attr(list) Attr(dict) List(of=...)
    """
    def store(self, val):
        """
        stores a json in the h5 metadata
        """
        val = json.dumps(val)
        self.owner.storage_manager.set_metadata({self.field_name: val})

    def load(self):
        val = self.owner.storage_manager.get_metadata()[self.field_name]
        return json.loads(val)



