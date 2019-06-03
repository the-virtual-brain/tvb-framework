import typing

if typing.TYPE_CHECKING:
    from tvb.basic.neotraits.api import HasTraits
    from tvb.core.neotraits.h5 import H5File
    from tvb.core.neotraits.db import HasTraitsIndex


class Registry(object):
    """
    A configuration class that holds the one to one relationship
    between datatypes and H5Files that can read/write them to disk
    """
    def __init__(self):
        self._datatype_for_h5file = {}
        self._h5file_for_datatype = {}
        self._index_for_datatype = {}
        self._datatype_for_index = {}

    def get_h5file_for_datatype(self, datatype_class):
        # type: (typing.Type[HasTraits]) -> typing.Type[H5File]
        return self._h5file_for_datatype[datatype_class]

    def get_datatype_for_h5file(self, h5file_class):
        # type: (typing.Type[H5File]) -> typing.Type[HasTraits]
        return self._datatype_for_h5file[h5file_class]

    def get_index_for_datatype(self, datatype_class):
        # type: (typing.Type[HasTraits]) -> typing.Type[HasTraitsIndex]
        return self._index_for_datatype[datatype_class]

    def get_datatype_for_index(self, index_class):
        # type: (typing.Type[HasTraitsIndex]) -> typing.Type[HasTraits]
        return self._datatype_for_index[index_class]

    def get_h5file_for_index(self, index_class):
        # type: (typing.Type[HasTraitsIndex]) -> typing.Type[H5File]
        return self._h5file_for_datatype[self._datatype_for_index[index_class]]

    def register_h5file_datatype(self, h5file_class, datatype_class, datatype_index):
        self._h5file_for_datatype[datatype_class] = h5file_class
        self._index_for_datatype[datatype_class] = datatype_index
        self._datatype_for_h5file[h5file_class] = datatype_class
        self._datatype_for_index[datatype_index] = datatype_class

