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

import importlib
import uuid
import typing
import os.path
import abc
import numpy
from datetime import datetime
from tvb.core.entities.file.exceptions import MissingDataSetException
from tvb.core.entities.file.hdf5_storage_manager import HDF5StorageManager
from tvb.basic.neotraits.api import HasTraits, Attr, NArray
from tvb.core.entities.generic_attributes import GenericAttributes
from tvb.core.utils import date2string


class Accessor(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, trait_attribute, h5file, name=None):
        # type: (Attr, H5File, str) -> None
        """
        :param trait_attribute: A traited attribute
        :param h5file: The parent H5file that contains this Accessor
        :param name: The name of the dataset or attribute in the h5 file.
                     It defaults to the name of the associated traited attribute.
                     If the traited attribute is not a member of a HasTraits then
                     it has no name and you have to provide this parameter
        """
        self.owner = h5file
        self.trait_attribute = trait_attribute

        if name is None:
            name = trait_attribute.field_name

        self.field_name = name

        if self.field_name is None:
            raise ValueError('Independent Accessor {} needs a name'.format(self))

    @abc.abstractmethod
    def load(self):
        pass

    @abc.abstractmethod
    def store(self, val):
        pass

    def __repr__(self):
        cls = type(self)
        return '<{}.{}({}, name="{}")>'.format(
            cls.__module__, cls.__name__, self.trait_attribute, self.field_name
        )


class Scalar(Accessor):
    """
    A scalar in a h5 file that corresponds to a traited attribute.
    Serialized as a global h5 attribute
    """

    def store(self, val):
        # type: (typing.Union[str, int, float]) -> None
        # noinspection PyProtectedMember
        val = self.trait_attribute._validate_set(None, val)
        self.owner.storage_manager.set_metadata({self.field_name: val})

    def load(self):
        # type: () -> typing.Union[str, int, float]
        # assuming here that the h5 will return the type we stored.
        # if paranoid do self.trait_attribute.field_type(value)
        return self.owner.storage_manager.get_metadata()[self.field_name]


class Uuid(Scalar):
    def store(self, val):
        # type: (uuid.UUID) -> None
        if val is None and not self.trait_attribute.required:
            # this is an optional reference and it is missing
            return
        # noinspection PyProtectedMember
        if not isinstance(val, uuid.UUID):
            raise TypeError("expected uuid.UUID got {}".format(type(val)))
        # urn is a standard encoding, that is obvious an uuid
        # str(gid) is more ambiguous
        self.owner.storage_manager.set_metadata({self.field_name: val.urn})

    def load(self):
        # type: () -> uuid.UUID
        # TODO: handle inexistent field?
        metadata = self.owner.storage_manager.get_metadata()
        if self.field_name in metadata:
            return uuid.UUID(metadata[self.field_name])
        return None


class DataSetMetaData(object):
    """
    simple container for dataset metadata
    Useful as a cache of global min max values.
    Viewers rely on these for colorbars.
    """

    # noinspection PyShadowingBuiltins
    def __init__(self, min, max, mean):
        self.min, self.max, self.mean = min, max, mean

    @classmethod
    def from_array(cls, array):
        try:
            return cls(min=array.min(), max=array.max(), mean=array.mean())
        except (TypeError, ValueError):
            # likely a string array
            return cls(min=None, max=None, mean=None)

    @classmethod
    def from_dict(cls, dikt):
        return cls(min=dikt['Minimum'], max=dikt['Maximum'], mean=dikt['Mean'])

    def to_dict(self):
        return {'Minimum': self.min, 'Maximum': self.max, 'Mean': self.mean}

    def merge(self, other):
        self.min = min(self.min, other.min)
        self.max = max(self.max, other.max)
        self.mean = (self.mean + other.mean) / 2


class DataSet(Accessor):
    """
    A dataset in a h5 file that corresponds to a traited NArray.
    """
    def __init__(self, trait_attribute, h5file, name=None, expand_dimension=-1):
        # type: (NArray, H5File, str, int) -> None
        """
        :param trait_attribute: A traited attribute
        :param h5file: The parent H5file that contains this Accessor
        :param name: The name of the dataset in the h5 file.
                     It defaults to the name of the associated traited attribute.
                     If the traited attribute is not a member of a HasTraits then
                     it has no name and you have to provide this parameter
        :param expand_dimension: An int designating a dimension of the array that may grow.
        """
        super(DataSet, self).__init__(trait_attribute, h5file, name)
        self.expand_dimension = expand_dimension

    def append(self, data, close_file=True, grow_dimension=None):
        # type: (numpy.ndarray, bool, int) -> None
        if not grow_dimension:
            grow_dimension = self.expand_dimension
        self.owner.storage_manager.append_data(
            self.field_name,
            data,
            grow_dimension=grow_dimension,
            close_file=close_file
        )
        # update the cached array min max metadata values
        new_meta = DataSetMetaData.from_array(numpy.array(data))
        meta_dict = self.owner.storage_manager.get_metadata(self.field_name)
        if meta_dict:
            meta = DataSetMetaData.from_dict(meta_dict)
            meta.merge(new_meta)
        else:
            # this must be a new file, nothing to merge, set the new meta
            meta = new_meta
        self.owner.storage_manager.set_metadata(meta.to_dict(), self.field_name)


    def store(self, data):
        # type: (numpy.ndarray) -> None
        # noinspection PyProtectedMember
        data = self.trait_attribute._validate_set(None, data)
        if data is None:
            return

        self.owner.storage_manager.store_data(self.field_name, data)
        # cache some array information
        self.owner.storage_manager.set_metadata(
            DataSetMetaData.from_array(data).to_dict(),
            self.field_name
        )

    def load(self):
        # type: () -> numpy.ndarray
        if not self.trait_attribute.required:
            return self.owner.storage_manager.get_data(self.field_name, ignore_errors=True)
        return self.owner.storage_manager.get_data(self.field_name)

    def __getitem__(self, data_slice):
        # type: (typing.Tuple[slice, ...]) -> numpy.ndarray
        return self.owner.storage_manager.get_data(self.field_name, data_slice)

    @property
    def shape(self):
        # type: () -> typing.Tuple[int]
        return self.owner.storage_manager.get_data_shape(self.field_name)

    def get_cached_metadata(self):
        """
        Returns cached properties of this dataset, like min max mean etc.
        This cache is useful for large, expanding datasets,
        when we want to avoid loading the whole dataset just to compute a max.
        """
        meta = self.owner.storage_manager.get_metadata(self.field_name)
        return DataSetMetaData.from_dict(meta)



class Reference(Uuid):
    """
    A reference to another h5 file
    Corresponds to a contained datatype
    """
    def store(self, val):
        # type: (HasTraits) -> None
        """
        The reference is stored as a gid in the metadata.
        :param val: a datatype or a uuid.UUID gid
        """
        if val is None and not self.trait_attribute.required:
            # this is an optional reference and it is missing
            return
        if isinstance(val, HasTraits):
            val = val.gid
        if not isinstance(val, uuid.UUID):
            raise TypeError("expected uuid.UUId or HasTraits, got {}".format(type(val)))
        super(Reference, self).store(val)



class H5File(object):
    """
    A H5 based file format.
    This class implements reading and writing to a *specific* h5 based file format.
    A subclass of this defines a new file format.
    """

    def __init__(self, path):
        # type: (str) -> None
        self.path = path
        storage_path, file_name = os.path.split(path)
        self.storage_manager = HDF5StorageManager(storage_path, file_name)
        # would be nice to have an opened state for the chunked api instead of the close_file=False

        # common scalar headers
        self.gid = Uuid(Attr(field_type=uuid.UUID), self, name='gid')
        self.written_by = Scalar(Attr(str), self, name='written_by')
        self.create_date = Scalar(Attr(str), self, name='create_date')

        # Generic attributes descriptors
        self.generic_attributes = GenericAttributes()
        self.invalid = Scalar(Attr(bool), self, name='invalid')
        self.is_nan = Scalar(Attr(bool), self, name='is_nan')
        self.subject = Scalar(Attr(basestring), self, name='subject')
        self.state = Scalar(Attr(basestring), self, name='state')
        self.type = Scalar(Attr(basestring), self, name='type')
        self.user_tag_1 = Scalar(Attr(basestring), self, name='user_tag_1')
        self.user_tag_2 = Scalar(Attr(basestring), self, name='user_tag_2')
        self.user_tag_3 = Scalar(Attr(basestring), self, name='user_tag_3')
        self.user_tag_4 = Scalar(Attr(basestring), self, name='user_tag_4')
        self.user_tag_5 = Scalar(Attr(basestring), self, name='user_tag_5')
        self.visible = Scalar(Attr(bool), self, name='visible')

    @classmethod
    def file_name_base(cls):
        return cls.__name__.replace("H5", "")

    def iter_accessors(self):
        # type: () -> typing.Generator[Accessor]
        for accessor in self.__dict__.itervalues():
            if isinstance(accessor, Accessor):
                yield accessor

    def iter_datasets(self):
        for dataset in self.__dict__.itervalues():
            if isinstance(dataset, DataSet):
                yield dataset

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.written_by.store(self.__class__.__module__ + '.' + self.__class__.__name__)
        self.storage_manager.close_file()

    def store(self, datatype, scalars_only=False, store_references=True):
        # type: (HasTraits, bool, bool) -> None
        for accessor in self.iter_accessors():
            f_name = accessor.trait_attribute.field_name
            if f_name is None:
                # skipp attribute that does not seem to belong to a traited type
                # accessor is an independent Accessor
                continue
            if scalars_only and not isinstance(accessor, Scalar):
                continue
            if not store_references and isinstance(accessor, Reference):
                continue
            accessor.store(getattr(datatype, f_name))

    def load_into(self, datatype):
        # type: (HasTraits) -> None
        for accessor in self.iter_accessors():
            if isinstance(accessor, Reference):
                # we do not load references recursively
                continue
            f_name = accessor.trait_attribute.field_name
            if f_name is None:
                # skipp attribute that does not seem to belong to a traited type
                continue

            # handle optional data, that will be missing from the h5 files
            try:
                value = accessor.load()
            except MissingDataSetException:
                if accessor.trait_attribute.required:
                    raise
                else:
                    value = None

            setattr(datatype, f_name, value)

    def store_generic_attributes(self, generic_attributes):
        # type: (GenericAttributes) -> None
        # write_metadata  creation time, serializer class name, etc
        self.create_date.store(date2string(datetime.now()))

        self.generic_attributes.fill_from(generic_attributes)
        self.invalid.store(self.generic_attributes.invalid)
        self.is_nan.store(self.generic_attributes.is_nan)
        self.subject.store(self.generic_attributes.subject)
        self.state.store(self.generic_attributes.state)
        self.type.store(self.generic_attributes.type)
        self.user_tag_1.store(self.generic_attributes.user_tag_1)
        self.user_tag_2.store(self.generic_attributes.user_tag_2)
        self.user_tag_3.store(self.generic_attributes.user_tag_3)
        self.user_tag_4.store(self.generic_attributes.user_tag_4)
        self.user_tag_5.store(self.generic_attributes.user_tag_5)
        self.visible.store(self.generic_attributes.visible)

    def load_generic_attributes(self):
        # type: () -> GenericAttributes
        self.generic_attributes.invalid = self.invalid.load()
        self.generic_attributes.is_nan = self.is_nan.load()
        self.generic_attributes.subject = self.subject.load()
        self.generic_attributes.state = self.state.load()
        self.generic_attributes.type = self.type.load()
        self.generic_attributes.user_tag_1 = self.user_tag_1.load()
        self.generic_attributes.user_tag_2 = self.user_tag_2.load()
        self.generic_attributes.user_tag_3 = self.user_tag_3.load()
        self.generic_attributes.user_tag_4 = self.user_tag_4.load()
        self.generic_attributes.user_tag_5 = self.user_tag_5.load()
        self.generic_attributes.visible = self.visible.load()
        return self.generic_attributes


    def gather_references(self):
        ret = []
        for accessor in self.iter_accessors():
            if isinstance(accessor, Reference):
                ret.append((accessor.trait_attribute.field_name, accessor.load()))
        return ret


    @staticmethod
    def from_file(path):
        # type: (str) -> typing.Type[H5File]
        base_dir, fname = os.path.split(path)
        storage_manager = HDF5StorageManager(base_dir, fname)
        meta = storage_manager.get_metadata()
        h5file_class_fqn = meta.get('written_by')
        package, cls_name = h5file_class_fqn.rsplit('.', 1)
        module = importlib.import_module(package)
        cls = getattr(module, cls_name)
        return cls(path)


    def __repr__(self):
        return '<{}("{}")>'.format(type(self).__name__, self.path)

