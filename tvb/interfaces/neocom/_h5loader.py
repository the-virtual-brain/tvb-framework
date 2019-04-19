import os
import uuid

import typing
from tvb.basic.neotraits.api import HasTraits
from .config import registry
from tvb.core.neotraits.h5 import H5File



class Loader(object):
    """
    A default simple loader. Does not do recursive loads. Loads stores just to paths.
    """

    def load(self, source):
        # type: (str) -> HasTraits

        with H5File.from_file(source) as f:
            datatype_cls = registry.get_datatype_for_h5file(type(f))
            datatype = datatype_cls()
            f.load_into(datatype)
            return datatype

    def store(self, datatype, destination):
        # type: (HasTraits, str) -> None
        h5file_cls = registry.get_h5file_for_datatype(type(datatype))

        with h5file_cls(destination) as f:
            f.store(datatype)



class DirLoader(object):
    """
    A simple recursive loader. Stores all files in a directory.
    You refer to files by their gid
    """
    def __init__(self, base_dir, recursive=False):
        # type: (str, bool) -> None
        if not os.path.isdir(base_dir):
            raise IOError('not a directory {}'.format(base_dir))

        self.base_dir = base_dir
        self.recursive = recursive


    def _locate(self, gid):
        # type: (uuid.UUID) -> str
        for fname in os.listdir(self.base_dir):
            if fname.endswith(gid.hex + '.h5'):
                return fname
        raise IOError('could not locate h5 with gid {}'.format(gid))


    def find_file_name(self, gid):
        # type: (typing.Union[uuid.UUID, str]) -> str
        if isinstance(gid, basestring):
            gid = uuid.UUID(gid)

        fname = self._locate(gid)
        return fname

    def load(self, gid):
        # type: (typing.Union[uuid.UUID, str]) -> HasTraits
        fname = self.find_file_name(gid)

        sub_dt_refs = []

        with H5File.from_file(os.path.join(self.base_dir, fname)) as f:
            datatype_cls = registry.get_datatype_for_h5file(type(f))
            datatype = datatype_cls()
            f.load_into(datatype)

            if self.recursive:
                sub_dt_refs = f.gather_references()

        for fname, sub_gid in sub_dt_refs:
            subdt = self.load(sub_gid)
            setattr(datatype, fname, subdt)

        return datatype


    def store(self, datatype):
        # type: (HasTraits) -> None
        h5file_cls = registry.get_h5file_for_datatype(type(datatype))
        path = self.path_for(h5file_cls, datatype.gid)

        sub_dt_refs = []

        with h5file_cls(path) as f:
            f.store(datatype)

            if self.recursive:
                sub_dt_refs = f.gather_references()

        for fname, sub_gid in sub_dt_refs:
            subdt = getattr(datatype, fname)
            self.store(subdt)


    def path_for(self, h5_file_class, gid):
        """
        where will this Loader expect to find a file of this format and with this gid
        """
        if isinstance(gid, basestring):
            gid = uuid.UUID(gid)
        datatype_cls = registry.get_datatype_for_h5file(h5_file_class)
        fname = '{}_{}.h5'.format(datatype_cls.__name__, gid.hex)
        return os.path.join(self.base_dir, fname)

