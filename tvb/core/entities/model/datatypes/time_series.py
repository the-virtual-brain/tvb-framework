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
from tvb.core.entities.model.datatypes.sensors import SensorsIndex
from tvb.core.entities.model.datatypes.connectivity import ConnectivityIndex
from tvb.core.entities.model.datatypes.region_mapping import RegionMappingIndex, RegionVolumeMappingIndex
from tvb.core.entities.model.datatypes.surface import SurfaceIndex
from tvb.core.entities.model.datatypes.volume import VolumeIndex
from tvb.core.entities.model.model_datatype import DataType


class TimeSeriesIndex(DataType):
    id = Column(Integer, ForeignKey(DataType.id), primary_key=True)

    title = Column(String)
    time_series_type = Column(String, nullable=False)
    data_ndim = Column(Integer, nullable=False)
    data_length_1d = Column(Integer)
    data_length_2d = Column(Integer)
    data_length_3d = Column(Integer)
    data_length_4d = Column(Integer)

    sample_period_unit = Column(String, nullable=False)
    sample_period = Column(Float, nullable=False)
    sample_rate = Column(Float)
    labels_ordering = Column(String, nullable=False)
    has_volume_mapping = Column(Boolean, nullable=False, default=False)
    has_surface_mapping = Column(Boolean, nullable=False, default=False)

    def fill_from_has_traits(self, datatype):
        # type: (TimeSeries)  -> None
        super(TimeSeriesIndex, self).fill_from_has_traits(datatype)
        self.title = datatype.title
        self.time_series_type = type(datatype).__name__
        self.sample_period_unit = datatype.sample_period_unit
        self.sample_period = datatype.sample_period
        self.sample_rate = datatype.sample_rate
        self.labels_ordering = json.dumps(datatype.labels_ordering)

        # REVIEW THIS.
        # In general constructing graphs here is a bad ideea
        # But these NArrayIndex-es can be treated as part of this entity
        # never to be referenced by any other row or table.
        self.data_ndim = datatype.data.ndim
        self.data_length_1d = datatype.data.shape[0]
        if self.data_ndim > 1:
            self.data_length_2d = datatype.data.shape[1]
            if self.data_ndim > 2:
                self.data_length_3d = datatype.data.shape[2]
                if self.data_ndim > 3:
                    self.data_length_4d = datatype.data.shape[3]

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


class TimeSeriesEEGIndex(TimeSeriesIndex):
    id = Column(Integer, ForeignKey(TimeSeriesIndex.id), primary_key=True)

    sensors_id = Column(Integer, ForeignKey(SensorsIndex.id), nullable=not TimeSeriesEEG.sensors.required)
    sensors = relationship(SensorsIndex, foreign_keys=sensors_id)


class TimeSeriesMEGIndex(TimeSeriesIndex):
    id = Column(Integer, ForeignKey(TimeSeriesIndex.id), primary_key=True)

    sensors_id = Column(Integer, ForeignKey(SensorsIndex.id), nullable=not TimeSeriesMEG.sensors.required)
    sensors = relationship(SensorsIndex, foreign_keys=sensors_id)


class TimeSeriesSEEGIndex(TimeSeriesIndex):
    id = Column(Integer, ForeignKey(TimeSeriesIndex.id), primary_key=True)

    sensors_id = Column(Integer, ForeignKey(SensorsIndex.id), nullable=not TimeSeriesSEEG.sensors.required)
    sensors = relationship(SensorsIndex, foreign_keys=sensors_id)


class TimeSeriesRegionIndex(TimeSeriesIndex):
    id = Column(Integer, ForeignKey(TimeSeriesIndex.id), primary_key=True)

    connectivity_id = Column(Integer, ForeignKey(ConnectivityIndex.id),
                             nullable=not TimeSeriesRegion.connectivity.required)
    connectivity = relationship(ConnectivityIndex, foreign_keys=connectivity_id)

    region_mapping_volume_id = Column(Integer, ForeignKey(RegionVolumeMappingIndex.id),
                                      nullable=not TimeSeriesRegion.region_mapping_volume.required)
    region_mapping_volume = relationship(RegionVolumeMappingIndex, foreign_keys=region_mapping_volume_id)

    region_mapping_id = Column(Integer, ForeignKey(RegionMappingIndex.id),
                               nullable=not TimeSeriesRegion.region_mapping.required)
    region_mapping = relationship(RegionMappingIndex, foreign_keys=region_mapping_id)


class TimeSeriesSurfaceIndex(TimeSeriesIndex):
    id = Column(Integer, ForeignKey(TimeSeriesIndex.id), primary_key=True)

    surface_id = Column(Integer, ForeignKey(SurfaceIndex.id), nullable=not TimeSeriesSurface.surface.required)
    surface = relationship(SurfaceIndex, foreign_keys=surface_id)


class TimeSeriesVolumeIndex(TimeSeriesIndex):
    id = Column(Integer, ForeignKey(TimeSeriesIndex.id), primary_key=True)

    volume_id = Column(Integer, ForeignKey(VolumeIndex.id), nullable=not TimeSeriesVolume.volume.required)
    volume = relationship(VolumeIndex, foreign_keys=volume_id)
