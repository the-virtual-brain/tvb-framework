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

import json
import numpy
import scipy.sparse
from ._h5core import DataSetMetaData, Accessor, Scalar


class SparseMatrixMetaData(DataSetMetaData):
    """
    Essential metadata for interpreting a sparse matrix stored in h5
    """

    def __init__(self, minimum, maximum, mean, format, dtype, shape):
        super(SparseMatrixMetaData, self).__init__(minimum, maximum, mean)
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
            mean=mtx.data.mean(),
            format=mtx.format,
            dtype=mtx.dtype,
            shape=mtx.shape,
        )

    @classmethod
    def from_dict(cls, dikt):
        return cls(
            minimum=dikt['Minimum'],
            maximum=dikt['Maximum'],
            mean=dikt['Mean'],
            format=dikt['format'],
            dtype=numpy.dtype(dikt['dtype']),
            shape=cls.parse_shape(dikt['Shape']),
        )

    def to_dict(self):
        return {
            'Minimum': self.min,
            'Maximum': self.max,
            'Mean': self.mean,
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

    def __init__(self, trait_attribute, h5file, name=None, json_encoder=None, json_decoder=None):
        super(Json, self).__init__(trait_attribute, h5file, name)
        self.json_encoder = json_encoder
        self.json_decoder = json_decoder

    def store(self, val):
        """
        stores a json in the h5 metadata
        """
        val = json.dumps(val, cls=self.json_encoder)
        self.owner.storage_manager.set_metadata({self.field_name: val})

    def load(self):
        val = self.owner.storage_manager.get_metadata()[self.field_name]
        if self.json_decoder:
            return self.json_decoder().decode(val)
        return json.loads(val)
