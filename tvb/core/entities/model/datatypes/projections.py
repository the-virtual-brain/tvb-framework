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
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from tvb.datatypes.projections import ProjectionMatrix
from tvb.core.entities.model.datatypes.sensors import SensorsIndex
from tvb.core.entities.model.datatypes.surface import SurfaceIndex
from tvb.core.entities.model.model_datatype import DataType


class ProjectionMatrixIndex(DataType):
    id = Column(Integer, ForeignKey(DataType.id), primary_key=True)

    projection_type = Column(String, nullable=False)

    brain_skull_id = Column(Integer, ForeignKey(SurfaceIndex.id), nullable=not ProjectionMatrix.brain_skull.required)
    brain_skull = relationship(SurfaceIndex, foreign_keys=brain_skull_id, primaryjoin=SurfaceIndex.id == brain_skull_id, cascade='none')

    skull_skin_id = Column(Integer, ForeignKey(SurfaceIndex.id), nullable=not ProjectionMatrix.skull_skin.required)
    skull_skin = relationship(SurfaceIndex, foreign_keys=skull_skin_id, primaryjoin=SurfaceIndex.id == skull_skin_id, cascade='none')

    skin_air_id = Column(Integer, ForeignKey(SurfaceIndex.id), nullable=not ProjectionMatrix.skin_air.required)
    skin_air = relationship(SurfaceIndex, foreign_keys=skin_air_id, primaryjoin=SurfaceIndex.id == skin_air_id, cascade='none')

    source_id = Column(Integer, ForeignKey(SurfaceIndex.id), nullable=not ProjectionMatrix.sources.required)
    source = relationship(SurfaceIndex, foreign_keys=source_id, primaryjoin=SurfaceIndex.id == source_id, cascade='none')

    sensors_id = Column(Integer, ForeignKey(SensorsIndex.id), nullable=not ProjectionMatrix.sensors.required)
    sensors = relationship(SensorsIndex, foreign_keys=sensors_id, primaryjoin=SensorsIndex.id == sensors_id, cascade='none')

    def fill_from_has_traits(self, datatype):
        # type: (ProjectionMatrix)  -> None
        super(ProjectionMatrixIndex, self).fill_from_has_traits(datatype)
        self.projection_type = datatype.projection_type