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
Service layer, for storing/retrieving Resulting Figures in TVB.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

import os
import base64
from tvb.basic.logger.builder import get_logger
from tvb.core import utils
from tvb.core.entities import model
from tvb.core.entities.storage import dao
from tvb.core.entities.file.fileshelper import FilesHelper



class FigureService:
    """
    Service layer for Figure entities.
    """


    def __init__(self):
        self.logger = get_logger(self.__class__.__module__)
        self.file_helper = FilesHelper()


    def store_result_figure(self, project, user, img_type, operation_id, export_data):
        """
        Store into a file, Result Image and reference in DB.
        """
        session_name = "Default"
        file_name = "snapshot." + img_type

        # Generate path where to store image
        store_path = self.file_helper.get_images_folder(project.name, operation_id)
        store_path = utils.get_unique_file_name(store_path, file_name)[0]
        file_name = os.path.split(store_path)[1]

        if img_type == "png":  # PNG file from canvas
            # Store image
            img_data = base64.b64decode(export_data)
            dest = open(store_path, 'wb')
            dest.write(img_data)
            dest.close()
        elif img_type == 'svg':  # SVG file from svg viewer
            # Generate path where to store image
            dest = open(store_path, 'w')
            dest.write(export_data)
            dest.close()

        # Store entity into DB
        entity = model.ResultFigure(operation_id, user.id, project.id, session_name,
                                    "Snapshot-" + operation_id, file_name, img_type)
        entity = dao.store_entity(entity)

        # Load instance from DB to have lazy fields loaded
        figure = dao.load_figure(entity.id)
        # Write image meta data to disk  
        self.file_helper.write_image_metadata(figure)

        # Force writing operation meta data on disk. 
        # This is important later for operation import
        operation = dao.get_operation_by_id(operation_id)
        self.file_helper.write_operation_metadata(operation)


    def retrieve_result_figures(self, project, user, selected_session_name='all_sessions'):
        """
        Retrieve from DB all the stored Displayer previews that belongs to the specified session. The
        previews are for current user and project; grouped by session.
        """
        result, previews_info = dao.get_previews(project.id, user.id, selected_session_name)
        for name in result:
            for figure in result[name]:
                figures_folder = self.file_helper.get_images_folder(project.name, figure.operation.id)
                figure_full_path = os.path.join(figures_folder, figure.file_path)
                # Compute the path 
                figure.file_path = utils.path2url_part(figure_full_path)
        return result, previews_info


    @staticmethod
    def load_figure(figure_id):
        """
        Loads a stored figure by its id.
        """
        return dao.load_figure(figure_id)


    def edit_result_figure(self, figure_id, **data):
        """
        Retrieve and edit a previously stored figure.
        """
        figure = dao.load_figure(figure_id)
        figure.session_name = data['session_name']
        figure.name = data['name']
        dao.store_entity(figure)

        # Load instance from DB to have lazy fields loaded.
        figure = dao.load_figure(figure_id)
        # Store figure meta data in an XML attached to the image.
        self.file_helper.write_image_metadata(figure)


    def remove_result_figure(self, figure_id):
        """
        Remove figure from DB and file storage.
        """
        figure = dao.load_figure(figure_id)

        # Delete all figure related files from disk.
        figures_folder = self.file_helper.get_images_folder(figure.project.name, figure.operation.id)
        path2figure = os.path.join(figures_folder, figure.file_path)
        if os.path.exists(path2figure):
            os.remove(path2figure)
            self.file_helper.remove_image_metadata(figure)

        # Remove figure reference from DB.
        result = dao.remove_entity(model.ResultFigure, figure_id)
        return result
        
        
        