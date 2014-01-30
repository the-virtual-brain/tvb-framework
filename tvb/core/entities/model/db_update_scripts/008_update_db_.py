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
Change of DB structure for TVB version 1.0.6.
.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
"""

from tvb.core.entities.storage import dao


def upgrade(_migrate_engine):
    """
    Renames image paths in order to be consistent with the project migration script
    """
    project_count = dao.get_all_projects(is_count=True)
    for project in dao.get_all_projects(page_end=project_count):
        # what user does get_previews require? is it possible for a project
        # to show different images depending on a user?
        grouped_figures , _ = dao.get_previews(project.id, project.administrator.id)
        figures = grouped_figures.values()

        for figure in figures:
            figure.file_path = figure.operation.id + '-' + figure.file_path

        dao.store_entities(figures)


def downgrade(_migrate_engine):
    """
    Not really needed at the db level. There is no project downgrade.
    If it were it would not rename images thus leave the paths in the db unchanged.
    """
