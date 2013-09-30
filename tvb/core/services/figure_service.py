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

.. moduleauthor:: Ciprian Tomoiaga <ciprian.tomoiaga@codemart.ro>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

import os
import Image
# See TVB-985
if not hasattr(Image, 'open'):
    from Image import Image
import base64
import xml.dom.minidom
from StringIO import StringIO
from tvb.basic.logger.builder import get_logger
from tvb.core import utils
from tvb.core.entities import model
from tvb.core.entities.storage import dao
from tvb.core.entities.file.files_helper import FilesHelper



class FigureService:
    """
    Service layer for Figure entities.
    """
    _TYPE_PNG = "png"
    _TYPE_SVG = "svg"

    _BRANDING_BAR_PNG = os.path.join(os.path.dirname(__file__), "resources", "branding_bar.png")
    _BRANDING_BAR_SVG = os.path.join(os.path.dirname(__file__), "resources", "branding_bar.svg")

    _DEFAULT_SESSION_NAME = "Default"
    _DEFAULT_IMAGE_FILE_NAME = "snapshot."


    def __init__(self):
        self.logger = get_logger(self.__class__.__module__)
        self.file_helper = FilesHelper()


    def store_result_figure(self, project, user, img_type, operation_id, export_data):
        """
        Store into a file, Result Image and reference in DB.
        """
        # Generate path where to store image
        store_path = self.file_helper.get_images_folder(project.name, operation_id)
        store_path = utils.get_unique_file_name(store_path, FigureService._DEFAULT_IMAGE_FILE_NAME + img_type)[0]
        file_path = os.path.split(store_path)[1]

        if img_type == FigureService._TYPE_PNG:                         # PNG file from canvas
            imgData = base64.b64decode(export_data)                     # decode the image
            fakeImgFile = StringIO(imgData)                             # PIL.Image only opens from file, so fake one
            origImg = Image.open(fakeImgFile)
            brandingBar = Image.open(FigureService._BRANDING_BAR_PNG)

            finalSize = (origImg.size[0],                               # original width
                         origImg.size[1] + brandingBar.size[1])         # original height + brandingBar height
            finalImg = Image.new("RGBA", finalSize)

            finalImg.paste(origImg, (0, 0))                             # add the original image
            finalImg.paste(brandingBar, (0, origImg.size[1]))           # add the branding bar, below the original
                                                                        # the extra width will be discarded

            finalImg.save(store_path)                                   # store to disk

        elif img_type == FigureService._TYPE_SVG:                                   # SVG file from svg viewer
            dom = xml.dom.minidom.parseString(export_data)
            figureSvg = dom.getElementsByTagName('svg')[0]                          # get the original image

            dom = xml.dom.minidom.parse(FigureService._BRANDING_BAR_SVG)
            brandingSvg = dom.getElementsByTagName('svg')[0]                        # get the branding bar
            brandingSvg.setAttribute("y", figureSvg.getAttribute("height"))         # position it below the figure

            finalSvg = dom.createElement('svg')                                     # prepare the final svg
            width = figureSvg.getAttribute('width').replace('px', '')               # same width as original figure
            finalSvg.setAttribute("width", width)
            height = float(figureSvg.getAttribute('height').replace('px', ''))      # increase original height with
            height += float(brandingSvg.getAttribute('height').replace('px', ''))   # branding bar's height
            finalSvg.setAttribute("height", str(height))

            finalSvg.appendChild(figureSvg)                                         # add the image
            finalSvg.appendChild(brandingSvg)                                       # and the branding bar

            # Generate path where to store image
            dest = open(store_path, 'w')
            finalSvg.writexml(dest)                                                 # store to disk
            dest.close()

        operation = dao.get_operation_by_id(operation_id)
        file_name = 'TVB-%s-%s' % (operation.algorithm.name.replace(' ', '-'), operation_id)    # e.g. TVB-Algo-Name-352

        # Store entity into DB
        entity = model.ResultFigure(operation_id, user.id, project.id, FigureService._DEFAULT_SESSION_NAME,
                                    file_name, file_path, img_type)
        entity = dao.store_entity(entity)

        # Load instance from DB to have lazy fields loaded
        figure = dao.load_figure(entity.id)
        # Write image meta data to disk  
        self.file_helper.write_image_metadata(figure)

        # Force writing operation meta data on disk. 
        # This is important later for operation import
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
        
        
        