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
.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
"""

import os
import csv
import numpy
from tvb.basic.traits.util import read_list_data
from tvb.basic.logger.builder import get_logger
from tvb.core.utils import store_list_data
from tvb.datatypes.connectivity import Connectivity
from tvb.core.adapters.abcadapter import ABCSynchronous
from tvb.core.adapters.exceptions import LaunchException
from tvb.core.entities.file.files_helper import FilesHelper
import demo_data.connectivity

class CSVConnectivityImporter(ABCSynchronous):
    """
    Handler for uploading a Connectivity archive, with files holding 
    text export of connectivity data from Numpy arrays.
    """
    _ui_name = "Connectivity CSV"
    _ui_subsection = "csv_connectivity_importer"
    _ui_description = "Import a Connectivity from two CSV files as result from the DTI pipeline"
    FILE_NODES_ORDER = "dti_pipeline_regions.txt"
    WEIGHTS_FILE = "weights.txt"
    TRACT_FILE = "tract_lengths.txt"


    def __init__(self):
        ABCSynchronous.__init__(self)
        self.logger = get_logger(self.__class__.__module__)
        folder_default_data = os.path.dirname(demo_data.connectivity.__file__)
        file_order = os.path.join(folder_default_data, self.FILE_NODES_ORDER)
        self.expected_nodes_order = read_list_data(file_order, dtype=numpy.int32, usecols=[0])

    
    
    def get_input_tree(self):
        """
        Take as input a ZIP archive.
        """
        return [{'name': 'weights', 'type': 'upload', 'label': 'Weights file (csv)', 'required': True},
                {'name': 'tracts', 'type': 'upload', 'label': 'Tracts file (csv)', 'required': True},
                {'name': 'input_data', 'label': 'Reference Connectivity Matrix (for node labels, 3d positions etc.)',
                 'type': Connectivity, 'required': True}]
        
        
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


    def _process_csv_file(self, csv_file, result_file):
        """
        Read a CSV file, arrange rows/columns in the correct order,
        to obtain Weight/Tract TXT files in TVB compatible format.
        """
        file_point = open(csv_file)
        csv_reader = csv.reader(file_point)

        ## Index of the current row (from 1 to the number of nodes + 2; as we have a header line):
        row_number = 0
        connectivity_size = len(self.expected_nodes_order)
        expected_indices = range(connectivity_size)
        result_conn = [[] for _ in xrange(connectivity_size)]

        for row in csv_reader:
            row_number += 1
            if len(row) != connectivity_size:
                msg = "Invalid Connectivity Row size! %d != %d at row %d" % (len(row), connectivity_size, row_number)
                raise LaunchException(msg)

            if row_number == 1:
                for i in xrange(connectivity_size):
                    found = False
                    for j in xrange(connectivity_size):
                        if self.expected_nodes_order[j] == int(row[i]):
                            expected_indices[i] = j
                            found = True
                            break
                    if not found:
                        msg = "Incompatible Title Row %d with expected labels %s \n %s "
                        msg = msg % (i, str(row), str(self.expected_nodes_order))
                        raise LaunchException(msg)
                continue

            new_row = [0] * connectivity_size
            for i in xrange(connectivity_size):
                new_row[expected_indices[i]] = float(row[i]) if float(row[i]) >= 0 else 0

            result_conn[expected_indices[row_number - 2]] = new_row

        if row_number != connectivity_size + 1:
            raise LaunchException("Invalid Connectivity size! %d != %d " % (row_number, connectivity_size))

        self.logger.debug("Written Connectivity file of size " + str(len(result_conn)))
        store_list_data(result_conn, result_file, os.path.dirname(csv_file), True)
        file_point.close()
        os.remove(csv_file)


    def launch(self, weights, tracts, input_data):
        """
        Execute import operations: process the weights and tracts csv files, then use
        the reference connectivity passed as input_data for the rest of the attributes.

        :param weights: csv file containing the weights measures
        :param tracts:  csv file containing the tracts measures
        :param input_data: a reference connectivity with the additional attributes

        :raises LaunchException: when the number of nodes in CSV files doesn't match the one in the connectivity
        """

        self._process_csv_file(weights, self.WEIGHTS_FILE)
        self._process_csv_file(tracts, self.TRACT_FILE)
        weights_matrix = read_list_data(os.path.join(os.path.dirname(weights), self.WEIGHTS_FILE))
        tract_matrix = read_list_data(os.path.join(os.path.dirname(tracts), self.TRACT_FILE))
        FilesHelper.remove_files([os.path.join(os.path.dirname(weights), self.WEIGHTS_FILE),
                                  os.path.join(os.path.dirname(tracts), self.TRACT_FILE)])

        if weights_matrix.shape[0] != input_data.orientations.shape[0]:
            raise LaunchException("The csv files define %s nodes but the connectivity you selected as reference "
                                  "has only %s nodes." % (weights_matrix.shape[0], input_data.orientations.shape[0]))
        result = Connectivity()
        result.storage_path = self.storage_path
        result.nose_correction = input_data.nose_correction
        result.centres = input_data.centres
        result.region_labels = input_data.region_labels
        result.weights = weights_matrix
        result.tract_lengths = tract_matrix
        result.orientations = input_data.orientations
        result.areas = input_data.areas
        result.cortical = input_data.cortical
        result.hemispheres = input_data.hemispheres
        return result

