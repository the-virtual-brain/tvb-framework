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
from tvb.datatypes.time_series import *
from sqlalchemy import Column, Integer, ForeignKey, String, Float, Boolean
from sqlalchemy.orm import relationship
from tvb.adapters.datatypes.db.sensors import SensorsIndex
from tvb.adapters.datatypes.db.connectivity import ConnectivityIndex
from tvb.adapters.datatypes.db.region_mapping import RegionMappingIndex, RegionVolumeMappingIndex
from tvb.adapters.datatypes.db.surface import SurfaceIndex
from tvb.adapters.datatypes.db.volume import VolumeIndex
from tvb.core.entities.model.model_datatype import DataType


class TimeSeriesIndex(DataType):
    id = Column(Integer, ForeignKey(DataType.id), primary_key=True)

    time_series_type = Column(String, nullable=False)
    data_ndim = Column(Integer, nullable=False)
    data_length_1d = Column(Integer)
    data_length_2d = Column(Integer)
    data_length_3d = Column(Integer)
    data_length_4d = Column(Integer)
    start_time = Column(Float, default=0)

    sample_period_unit = Column(String, nullable=False)
    sample_period = Column(Float, nullable=False)
    sample_rate = Column(Float)
    labels_ordering = Column(String, nullable=False)
    labels_dimensions = Column(String, nullable=False)
    has_volume_mapping = Column(Boolean, nullable=False, default=False)
    has_surface_mapping = Column(Boolean, nullable=False, default=False)

    def fill_from_has_traits(self, datatype):
        # type: (TimeSeries)  -> None
        super(TimeSeriesIndex, self).fill_from_has_traits(datatype)
        self.title = datatype.title
        self.time_series_type = type(datatype).__name__
        self.start_time = datatype.start_time
        self.sample_period_unit = datatype.sample_period_unit
        self.sample_period = datatype.sample_period
        self.sample_rate = datatype.sample_rate
        self.labels_ordering = json.dumps(datatype.labels_ordering)
        self.labels_dimensions = json.dumps(datatype.labels_dimensions)

        # REVIEW THIS.
        # In general constructing graphs here is a bad ideea
        # But these NArrayIndex-es can be treated as part of this entity
        # never to be referenced by any other row or table.
        if hasattr(datatype, 'data'):
            self.data_ndim = datatype.data.ndim
            self.data_length_1d = datatype.data.shape[0]
            if self.data_ndim > 1:
                self.data_length_2d = datatype.data.shape[1]
                if self.data_ndim > 2:
                    self.data_length_3d = datatype.data.shape[2]
                    if self.data_ndim > 3:
                        self.data_length_4d = datatype.data.shape[3]

    def fill_shape(self, final_shape):
        self.data_ndim = len(final_shape)
        self.data_length_1d = final_shape[0]
        if self.data_ndim > 1:
            self.data_length_2d = final_shape[1]
            if self.data_ndim > 2:
                self.data_length_3d = final_shape[2]
                if self.data_ndim > 3:
                    self.data_length_4d = final_shape[3]

    @staticmethod
    def accepted_filters():
        filters = DataType.accepted_filters()
        filters.update(
            {'datatype_class.data_ndim': {'type': 'int', 'display': 'No of Dimensions', 'operations': ['==', '<', '>']},
             'datatype_class.sample_period': {'type': 'float', 'display': 'Sample Period',
                                              'operations': ['==', '<', '>']},
             'datatype_class.sample_rate': {'type': 'float', 'display': 'Sample Rate', 'operations': ['==', '<', '>']},
             'datatype_class.title': {'type': 'string', 'display': 'Title', 'operations': ['==', '!=', 'like']}
             })

        return filters

    def get_data_shape(self):
        if self.data_ndim == 1:
            return self.data_length_1d
        if self.data_ndim == 2:
            return self.data_length_1d, self.data_length_2d
        if self.data_ndim == 3:
            return self.data_length_1d, self.data_length_2d, self.data_length_3d
        return self.data_length_1d, self.data_length_2d, self.data_length_3d, self.data_length_4d

    def get_labels_for_dimension(self, idx):
        label_dimensions = json.loads(self.labels_dimensions)
        labels_ordering = json.loads(self.labels_ordering)
        return label_dimensions.get(labels_ordering[idx], [])


class TimeSeriesEEGIndex(TimeSeriesIndex):
    id = Column(Integer, ForeignKey(TimeSeriesIndex.id), primary_key=True)

    sensors_gid = Column(String(32), ForeignKey(SensorsIndex.gid), nullable=not TimeSeriesEEG.sensors.required)
    sensors = relationship(SensorsIndex, foreign_keys=sensors_gid)

    def fill_from_has_traits(self, datatype):
        # type: (TimeSeriesEEG)  -> None
        super(TimeSeriesEEGIndex, self).fill_from_has_traits(datatype)
        self.sensors_gid = datatype.sensors.gid.hex


class TimeSeriesMEGIndex(TimeSeriesIndex):
    id = Column(Integer, ForeignKey(TimeSeriesIndex.id), primary_key=True)

    sensors_gid = Column(String(32), ForeignKey(SensorsIndex.gid), nullable=not TimeSeriesMEG.sensors.required)
    sensors = relationship(SensorsIndex, foreign_keys=sensors_gid)

    def fill_from_has_traits(self, datatype):
        # type: (TimeSeriesMEG)  -> None
        super(TimeSeriesMEGIndex, self).fill_from_has_traits(datatype)
        self.sensors_gid = datatype.sensors.gid.hex


class TimeSeriesSEEGIndex(TimeSeriesIndex):
    id = Column(Integer, ForeignKey(TimeSeriesIndex.id), primary_key=True)

    sensors_gid = Column(String(32), ForeignKey(SensorsIndex.gid), nullable=not TimeSeriesSEEG.sensors.required)
    sensors = relationship(SensorsIndex, foreign_keys=sensors_gid)

    def fill_from_has_traits(self, datatype):
        # type: (TimeSeriesSEEG)  -> None
        super(TimeSeriesSEEGIndex, self).fill_from_has_traits(datatype)
        self.sensors_gid = datatype.sensors.gid.hex


class TimeSeriesRegionIndex(TimeSeriesIndex):
    id = Column(Integer, ForeignKey(TimeSeriesIndex.id), primary_key=True)

    connectivity_gid = Column(String(32), ForeignKey(ConnectivityIndex.gid),
                              nullable=not TimeSeriesRegion.connectivity.required)
    connectivity = relationship(ConnectivityIndex, foreign_keys=connectivity_gid,
                                primaryjoin=ConnectivityIndex.gid == connectivity_gid)

    region_mapping_volume_gid = Column(String(32), ForeignKey(RegionVolumeMappingIndex.gid),
                                       nullable=not TimeSeriesRegion.region_mapping_volume.required)
    region_mapping_volume = relationship(RegionVolumeMappingIndex, foreign_keys=region_mapping_volume_gid,
                                         primaryjoin=RegionVolumeMappingIndex.gid==region_mapping_volume_gid)

    region_mapping_gid = Column(String(32), ForeignKey(RegionMappingIndex.gid),
                                nullable=not TimeSeriesRegion.region_mapping.required)
    region_mapping = relationship(RegionMappingIndex, foreign_keys=region_mapping_gid,
                                  primaryjoin=RegionMappingIndex.gid==region_mapping_gid)

    def fill_from_has_traits(self, datatype):
        # type: (TimeSeriesRegion)  -> None
        super(TimeSeriesRegionIndex, self).fill_from_has_traits(datatype)
        self.connectivity_gid = datatype.connectivity.gid.hex
        if datatype.region_mapping_volume is not None:
            self.region_mapping_volume_gid = datatype.region_mapping_volume.gid.hex
            self.has_volume_mapping = True
        if datatype.region_mapping is not None:
            self.region_mapping_gid = datatype.region_mapping.gid.hex
            self.has_surface_mapping = True


class TimeSeriesSurfaceIndex(TimeSeriesIndex):
    id = Column(Integer, ForeignKey(TimeSeriesIndex.id), primary_key=True)

    surface_gid = Column(String(32), ForeignKey(SurfaceIndex.gid), nullable=not TimeSeriesSurface.surface.required)
    surface = relationship(SurfaceIndex, foreign_keys=surface_gid)

    def fill_from_has_traits(self, datatype):
        # type: (TimeSeriesSurface)  -> None
        super(TimeSeriesSurfaceIndex, self).fill_from_has_traits(datatype)
        self.surface_gid = datatype.surface.gid.hex
        self.has_surface_mapping = True


class TimeSeriesVolumeIndex(TimeSeriesIndex):
    id = Column(Integer, ForeignKey(TimeSeriesIndex.id), primary_key=True)

    volume_gid = Column(String(32), ForeignKey(VolumeIndex.gid), nullable=not TimeSeriesVolume.volume.required)
    volume = relationship(VolumeIndex, foreign_keys=volume_gid)

    def fill_from_has_traits(self, datatype):
        # type: (TimeSeriesVolume)  -> None
        super(TimeSeriesVolumeIndex, self).fill_from_has_traits(datatype)
        self.has_volume_mapping = True
        self.volume_gid = datatype.volume.gid.hex
