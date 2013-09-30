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
.. moduleauthor:: Calin Pavel <calin.pavel@codemart.ro>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

from tvb.core.adapters.abcadapter import ABCSynchronous
from tvb.core.entities.file.files_helper import FilesHelper
from tvb.basic.traits.util import read_list_data
from tvb.datatypes.connectivity import Connectivity
from tvb.core.adapters.exceptions import LaunchException
import numpy


class ZIPConnectivityImporter(ABCSynchronous):
    """
    Handler for uploading a Connectivity archive, with files holding 
    text export of connectivity data from Numpy arrays.
    """
    _ui_name = "Connectivity ZIP"
    _ui_subsection = "zip_connectivity_importer"
    _ui_description = "Import a Connectivity from ZIP"
    
    WEIGHT_TOKEN = "weight"
    POSITION_TOKEN = "position"
    TRACT_TOKEN = "tract"
    ORIENTATION_TOKEN = "orientation"
    AREA_TOKEN = "area"
    CORTICAL_INFO = "cortical"
    HEMISPHERE_INFO = "hemisphere"
            
    def __init__(self):
        ABCSynchronous.__init__(self)
    
    
    def get_input_tree(self):
        """
        Take as input a ZIP archive.
        """
        return [{'name': 'uploaded', 'type': 'upload', 'required_type': 'application/zip',
                 'label': 'Connectivity file (zip)', 'required': True},
                {'name': 'rotate_x', 'label': 'Rotate x', 'type': 'int', 'default': 0, 'minValue': 0, 'maxValue': 360},
                {'name': 'rotate_y', 'label': 'Rotate y', 'type': 'int', 'default': 0, 'minValue': 0, 'maxValue': 360},
                {'name': 'rotate_z', 'label': 'Rotate z', 'type': 'int', 'default': 0, 'minValue': 0, 'maxValue': 360}]
        
        
    def get_output(self):
        return [Connectivity]
    
    
    def get_required_memory_size(self, **kwargs):
        """
        Return the required memory to run this algorithm.
        """
        # Don't know how much memory is needed.
        return -1
    
    def get_required_disk_size(self, **kwargs):
        """
        Returns the required disk size to be able to run the adapter.
        """
        return 0

    def launch(self, uploaded, rotate_x=0, rotate_y=0, rotate_z=0):
        """
        Execute import operations: unpack ZIP and build Connectivity object as result.

        :param uploaded: an archive containing the Connectivity data to be imported

        :returns: `Connectivity`

        :raises LaunchException: when `uploaded` is empty or nonexistent
        :raises Exception: when
                    * weights or tracts matrix is invalid (negative values, wrong shape)
                    * any of the vector orientation, areas, cortical or hemisphere is \
                      different from the expected number of nodes
        """
        if uploaded is None:
            raise LaunchException("Please select ZIP file which contains data to import")
        
        files = FilesHelper().unpack_zip(uploaded, self.storage_path)
        
        weights_matrix = None
        centres = None
        labels_vector = None
        tract_matrix = None
        orientation = None
        areas = None
        cortical_vector = None
        hemisphere_vector = None
        
        for file_name in files:
            if file_name.lower().find(self.WEIGHT_TOKEN) >= 0:
                weights_matrix = read_list_data(file_name)
                continue
            if file_name.lower().find(self.POSITION_TOKEN) >= 0:
                centres = read_list_data(file_name, skiprows=1, usecols=[1, 2, 3])
                labels_vector = read_list_data(file_name, dtype=numpy.str, skiprows=1, usecols=[0])
                continue
            if file_name.lower().find(self.TRACT_TOKEN) >= 0:
                tract_matrix = read_list_data(file_name)
                continue
            if file_name.lower().find(self.ORIENTATION_TOKEN) >= 0:
                orientation = read_list_data(file_name)
                continue
            if file_name.lower().find(self.AREA_TOKEN) >= 0:
                areas = read_list_data(file_name)
                continue
            if file_name.lower().find(self.CORTICAL_INFO) >= 0:
                cortical_vector = read_list_data(file_name, dtype=numpy.bool)
                continue
            if file_name.lower().find(self.HEMISPHERE_INFO) >= 0:
                hemisphere_vector = read_list_data(file_name, dtype=numpy.bool)
                continue
        ### Clean remaining text-files.
        FilesHelper.remove_files(files, True)
        
        result = Connectivity()
        result.storage_path = self.storage_path
        result.nose_correction = [rotate_x, rotate_y, rotate_z]
        
        ### Fill positions
        if centres is None:
            raise Exception("Positions for Connectivity Regions are required! "
                            "We expect a file *position* inside the uploaded ZIP.")
        expected_number_of_nodes = len(centres)
        if expected_number_of_nodes < 2:
            raise Exception("A connectivity with at least 2 nodes is expected")
        result.centres = centres
        if labels_vector is not None:
            result.region_labels = labels_vector
            
        ### Fill and check weights
        if weights_matrix is not None:
            if numpy.any([x < 0 for x in weights_matrix.flatten()]):
                raise Exception("Negative values are not accepted in weights matrix! "
                                "Please check your file, and use values >= 0")
            if weights_matrix.shape != (expected_number_of_nodes, expected_number_of_nodes):
                raise Exception("Unexpected shape for weights matrix! "
                                "Should be %d x %d " % (expected_number_of_nodes, expected_number_of_nodes))
            result.weights = weights_matrix
            
        ### Fill and check tracts    
        if tract_matrix is not None:
            if numpy.any([x < 0 for x in tract_matrix.flatten()]):
                raise Exception("Negative values are not accepted in tracts matrix! "
                                "Please check your file, and use values >= 0")
            if tract_matrix.shape != (expected_number_of_nodes, expected_number_of_nodes):
                raise Exception("Unexpected shape for tracts matrix! "
                                "Should be %d x %d " % (expected_number_of_nodes, expected_number_of_nodes))
            result.tract_lengths = tract_matrix
        
        
        if orientation is not None:
            if len(orientation) != expected_number_of_nodes:
                raise Exception("Invalid size for vector orientation. "
                                "Expected the same as region-centers number %d" % expected_number_of_nodes)
            result.orientations = orientation
            
        if areas is not None:
            if len(areas) != expected_number_of_nodes:
                raise Exception("Invalid size for vector areas. "
                                "Expected the same as region-centers number %d" % expected_number_of_nodes)
            result.areas = areas
            
        if cortical_vector is not None:
            if len(cortical_vector) != expected_number_of_nodes:
                raise Exception("Invalid size for vector cortical. "
                                "Expected the same as region-centers number %d" % expected_number_of_nodes)
            result.cortical = cortical_vector
            
        if hemisphere_vector is not None:
            if len(hemisphere_vector) != expected_number_of_nodes:
                raise Exception("Invalid size for vector hemispheres. "
                                "Expected the same as region-centers number %d" % expected_number_of_nodes)
            result.hemispheres = hemisphere_vector
        return result


