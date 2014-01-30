# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and 
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
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

"""
Migrations for project structure
.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
"""
from tvb.basic.config.settings import TVBSettings
from tvb.basic.logger.builder import get_logger
from tvb.core.entities.file.files_helper import FilesHelper
from tvb.core.services.project_migration import migrate_0_to_1
logger = get_logger(__name__)

# list all migration functions here
_PROJECT_MIGRATIONS = [
    migrate_0_to_1.migrate,
]

def _run_migration(project_path, from_version, to_version):
    if not 0 < to_version <= len(_PROJECT_MIGRATIONS):
        raise ValueError(
            "Missing migration scripts from version "
            "%s to version %s" % (len(_PROJECT_MIGRATIONS), to_version))
    if from_version > to_version:
        raise ValueError("Cannot downgrade")

    for i in xrange(from_version, to_version):
        logger.info("migrating project zip from project version %s to %s" % (i, i + 1))
        _PROJECT_MIGRATIONS[i](project_path)


def migrate_project_unsafe(project_path):
    """
    Upgrades a tvb project structure.
    If it fails project_path will be in an undefined state
    The caller has todo a defensive copy
    """
    files_helper = FilesHelper()
    # This assumes that old project metadata file can be parsed by current version.
    project_meta = files_helper.read_project_metadata(project_path)
    from_version = project_meta.get('version', 0)
    to_version = TVBSettings.PROJECT_VERSION
    _run_migration(project_path, from_version, to_version)
    # update project version in metadata
    project_meta['version'] = to_version
    files_helper.write_project_metadata_from_dict(project_path, project_meta)