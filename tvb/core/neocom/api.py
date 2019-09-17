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

import os
import uuid
from .config import registry
from tvb.core.entities.storage import dao
from tvb.core.entities.file.files_helper import FilesHelper


class TVBLoader(object):

    def __init__(self):
        self.file_handler = FilesHelper()

    def path_for_stored_index(self, dt_index_instance):
        """ Given a Datatype(HasTraitsIndex) instance, build where the corresponding H5 should be or is stored"""
        operation = dao.get_operation_by_id(dt_index_instance.fk_from_operation)
        operation_folder = self.file_handler.get_project_folder(operation.project, str(operation.id))

        gid = uuid.UUID(dt_index_instance.gid)
        h5_file_class = registry.get_h5file_for_index(dt_index_instance.__class__)
        fname = '{}_{}.h5'.format(h5_file_class.file_name_base(), gid.hex)

        return os.path.join(operation_folder, fname)

    def path_for(self, operation_dir, h5_file_class, gid):
        if isinstance(gid, basestring):
            gid = uuid.UUID(gid)
        fname = '{}_{}.h5'.format(h5_file_class.file_name_base(), gid.hex)
        return os.path.join(operation_dir, fname)
