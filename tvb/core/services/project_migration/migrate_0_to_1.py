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

"""
Images have been moved in the project folder.
An associated db migration will update file paths in the db.
.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
"""

import shutil
import os
from tvb.core.entities.file.files_helper import FilesHelper
from tvb.core.entities.file.xml_metadata_handlers import XMLReader, XMLWriter

IMAGES_FOLDER = FilesHelper.IMAGES_FOLDER
TVB_OPERARATION_FILE = FilesHelper.TVB_OPERARATION_FILE
TVB_FILE_EXTENSION = FilesHelper.TVB_FILE_EXTENSION


def _rewrite_img_meta(pth, op_id):
    figure_dict = XMLReader(pth).read_metadata()
    figure_dict['file_path'] = op_id + '-' + figure_dict['file_path']
    XMLWriter(figure_dict).write(pth)


def _rename_images(op_id, img_path):
    """
    Prepend operationid to image names to make them unique.
    This is good enough for migration.
    """
    for f in os.listdir(img_path):
        new_name = op_id + '-' + f
        src_pth = os.path.join(img_path, f)
        dst_pth = os.path.join(img_path, new_name)

        if f.endswith(TVB_FILE_EXTENSION):
            _rewrite_img_meta(src_pth, op_id)
        os.rename(src_pth, dst_pth)


def _move_images(img_path, new_img_path):
    for f in os.listdir(img_path):
        shutil.move(os.path.join(img_path, f), os.path.join(new_img_path, f))


def migrate(project_path):
    """
    Images have been moved in the project folder.
    An associated db migration will update file paths in the db.
    """
    new_img_path = os.path.join(project_path, IMAGES_FOLDER)
    FilesHelper().check_created(new_img_path)

    for root, dirs, files in os.walk(project_path):
        in_operation_dir_with_images = IMAGES_FOLDER in dirs and TVB_OPERARATION_FILE in files
        if in_operation_dir_with_images:
            op_id = os.path.basename(root)
            img_path = os.path.join(root, IMAGES_FOLDER)
            _rename_images(op_id, img_path)
            _move_images(img_path, new_img_path)
            os.rmdir(img_path)
