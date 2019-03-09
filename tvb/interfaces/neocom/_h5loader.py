import os
import importlib
import uuid

import typing
from tvb.basic.neotraits.api import HasTraits
from tvb.core.entities.file.hdf5_storage_manager import HDF5StorageManager
from .config import registry

if typing.TYPE_CHECKING:
    from tvb.core.neotraits.h5 import H5File


def get_h5file_class(storage_manager):
    # type: (HDF5StorageManager) -> typing.Type[H5File]
    meta = storage_manager.get_metadata()
    h5file_class_fqn = meta.get('written_by')
    package, cls_name = h5file_class_fqn.rsplit('.', 1)
    module = importlib.import_module(package)
    return getattr(module, cls_name)


class Loader(object):
    """
    A default simple loader. Does not do recursive loads. Loads stores just to paths.
    """

    def load(self, source):
        # type: (str) -> HasTraits
        base_dir, fname = os.path.split(source)
        storage_manager = HDF5StorageManager(base_dir, fname)
        h5file_cls = get_h5file_class(storage_manager)

        with h5file_cls(os.path.join(base_dir, fname)) as f:
            datatype_cls = registry.get_datatype_for_h5file(h5file_cls)
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
            if fname.endswith(str(gid) + '.h5'):
                return fname
        raise IOError('could not locate h5 with gid {}'.format(gid))


    def load(self, gid):
        # type: (typing.Union[uuid.UUID, str]) -> HasTraits
        if isinstance(gid, basestring):
            gid = uuid.UUID(gid)

        fname = self._locate(gid)
        storage_manager = HDF5StorageManager(self.base_dir, fname)
        h5file_cls = get_h5file_class(storage_manager)

        sub_dt_refs = []

        with h5file_cls(os.path.join(self.base_dir, fname)) as f:
            datatype_cls = registry.get_datatype_for_h5file(h5file_cls)
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
        fname = '{}_{}.h5'.format(type(datatype).__name__, datatype.gid)

        sub_dt_refs = []

        with h5file_cls(os.path.join(self.base_dir, fname)) as f:
            f.store(datatype)

            if self.recursive:
                sub_dt_refs = f.gather_references()

        for fname, sub_gid in sub_dt_refs:
            subdt = getattr(datatype, fname)
            self.store(subdt)
