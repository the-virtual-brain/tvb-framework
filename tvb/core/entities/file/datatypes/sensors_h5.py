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
from tvb.basic.neotraits.api import NArray
from tvb.core.neotraits.h5 import H5File, DataSet, Scalar, STORE_STRING, MEMORY_STRING
from tvb.datatypes.sensors import Sensors


class SensorsH5(H5File):
    def __init__(self, path):
        super(SensorsH5, self).__init__(path)
        self.sensors_type = Scalar(Sensors.sensors_type, self)
        self.labels = DataSet(NArray(dtype=STORE_STRING), self, "labels")
        self.locations = DataSet(Sensors.locations, self)
        self.has_orientation = Scalar(Sensors.has_orientation, self)
        self.orientations = DataSet(Sensors.orientations, self)
        self.number_of_sensors = Scalar(Sensors.number_of_sensors, self)
        self.usable = DataSet(Sensors.usable, self)

    def get_locations(self):
        return self.locations.load()

    def get_labels(self):
        return self.labels.load()

    def store(self, datatype, scalars_only=False, store_references=False):
        # type: (Sensors, bool, bool) -> None
        super(SensorsH5, self).store(datatype, scalars_only, store_references)
        self.labels.store(datatype.labels.astype(STORE_STRING))

    def load_into(self, datatype):
        # type: (Sensors) -> None
        super(SensorsH5, self).load_into(datatype)
        datatype.labels = self.labels.load().astype(MEMORY_STRING)
