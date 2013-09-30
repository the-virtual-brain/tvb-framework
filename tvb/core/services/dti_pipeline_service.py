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
Commands with remove machine are grouped here.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""
import os
import csv
import numpy
import zipfile
import thread
import demo_data.connectivity as demo_root
import tvb.core.utils as utils
from tvb.basic.traits.util import read_list_data
from tvb.basic.config.settings import TVBSettings
from tvb.basic.logger.builder import get_logger
from tvb.core.entities.file.files_helper import FilesHelper
from tvb.core.services.flow_service import FlowService
from tvb.core.services.exceptions import ConnectException



class DTIPipelineService():
    """
    Service for basic localMachine - remoteMachine communication.
    It requires a remoteIP and remoteUsername.
    !!! The machines need to be setup in a way that SSH and SCP can function without asking for a password!!!
    """
    
    REMOTE_COPY = "scp %s %s@%s:%s"
    REMOTE_COPY_REVERSE = "scp %s@%s:%s %s"
    REMOTE_COMMAND = 'ssh %s@%s "%s"'
    
    DTI_PIPELINE_COMMAND = ("cd /home/erin/processing/; "
                            "./pipeline_start --dst %s --seg %s --sid 42 --pevX %s --pevY %s --pevZ %s "
                            "--img %s --fa %s --md %s --wm 3 --gm 4 --threads %d")
    
    CONNECTIVITY_IMPORTER = ["tvb.adapters.uploaders.zip_connectivity_importer", "ZIPConnectivityImporter"]
    
    FILE_NODES_ORDER = "dti_pipeline_regions.txt"
    CONNECTIVITY_DEFAULT = "connectivity_regions_96.zip"
    WEIGHTS_FILE = "weights.txt"
    TRACT_FILE = "tract_lengths.txt"
    REMOTE_WEIGHTS_FILE = "_ConnectionCapacityMatrix.csv"
    REMOTE_TRACT_FILE = "_ConnectionDistanceMatrix.csv"
    
    
    def __init__(self, remote_machine=None, remote_user=None):
        """
        :param remote_machine: IP for the remote machine
        :param remote_user: Username valid on remote_machine. No further password should be needed for connecting.
        """
        self.logger = get_logger(self.__class__.__module__)
        self.remote_machine = remote_machine
        self.remote_user = remote_user
        self.flow_service = FlowService()
        self.file_handler = FilesHelper()
        
        folder_default_data = os.path.dirname(demo_root.__file__)
        file_order = os.path.join(folder_default_data, self.FILE_NODES_ORDER)
        self.expected_nodes_order = read_list_data(file_order, dtype=numpy.int32, usecols=[0])
        
        zip_path = os.path.join(folder_default_data, self.CONNECTIVITY_DEFAULT)
        if not (os.path.exists(zip_path) and os.path.isfile(zip_path)):
            raise ConnectException("Could not find default Connectivity for the pipeline! " + str(zip_path))
        self.default_connectivity_zip_path = zip_path
        
    
    def _copy_file_remote(self, local_path, remote_path):
        """
        Copy one file from local machine to remote machine.
        
        :param local_path: valid file path on local machine
        :param remote_path: valid remote folder with write access, to SCP local file there.
        """
        try:
            command = self.REMOTE_COPY % (local_path, self.remote_user, self.remote_machine, remote_path)
            # self.logger.debug("Executing: " + command)
            os.system(command)
        except Exception, excep:
            self.logger.exception(excep)
            raise ConnectException("Could not copy file remote!! " + str(local_path) + " - " + str(remote_path), excep)
    
    
    def _copy_file_from_remote(self, remote_path, local_path):
        """
        Copy file from a remote machine to local machine.
        
        :param remote_path: valid file path on a remote machine.
        :param local_path: valid local folder, or non-existing file-name, where to copy remote file.
        """
        try:
            command = self.REMOTE_COPY_REVERSE % (self.remote_user, self.remote_machine, remote_path, local_path)
            self.logger.debug("Executing: " + command)
            os.system(command)
            if os.path.exists(local_path) and os.path.isfile(local_path):
                return local_path
            if os.path.exists(local_path) and os.path.isdir(local_path):
                return os.path.join(local_path, os.path.split(remote_path)[1])
            raise ConnectException("File was not copy!!!" + str(remote_path) + " - " + str(local_path))
        except Exception, excep:
            self.logger.exception(excep)
            raise ConnectException("Could not copy file!! " + str(remote_path) + " - " + str(local_path), excep)
    
    
    def _execute_remote(self, remote_command):
        """
        Execute command on a remote machine and wait for the command to finish.
        
        :param remote_command: String representing command to be executed remote. 
        """
        try:
            filled_command = self.REMOTE_COMMAND % (self.remote_user, self.remote_machine, remote_command)
            self.logger.debug("Executing remote: " + filled_command)
            os.system(filled_command)
        except Exception, excep:
            self.logger.exception(excep)
            raise ConnectException("Could not execute command remote!! " + str(remote_command), excep)
        
    
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
        expected_indices = [i for i in range(connectivity_size)]
        result_conn = [[] for _ in range(connectivity_size)]

        for row in csv_reader:
            row_number += 1
            if len(row) != connectivity_size:
                msg = "Invalid Connectivity Row size! %d != %d at row %d" % (len(row), connectivity_size, row_number)
                raise ConnectException(msg)
            
            if row_number == 1:
                for i in range(connectivity_size):
                    found = False
                    for j in range(connectivity_size):
                        if self.expected_nodes_order[j] == int(row[i]):
                            expected_indices[i] = j
                            found = True
                            break
                    if not found:
                        msg = "Incompatible Title Row %d with expected labels %s \n %s "
                        msg = msg % (i, str(row), str(self.expected_nodes_order))
                        raise ConnectException(msg)
                continue
                
            new_row = [0 for _ in range(connectivity_size)]
            for i in range(connectivity_size):
                new_row[expected_indices[i]] = float(row[i]) if float(row[i]) >= 0 else 0

            result_conn[expected_indices[row_number - 2]] = new_row
            
        if row_number != connectivity_size + 1:
            raise ConnectException("Invalid Connectivity size! %d != %d " % (row_number, connectivity_size))

        self.logger.debug("Written Connectivity file of size " + str(len(result_conn)))
        utils.store_list_data(result_conn, result_file, os.path.dirname(csv_file), True)
        file_point.close()
        os.remove(csv_file)
        
     
    def _process_input_zip(self, zip_arch, result_folder, remote_prefix, 
                           file_name_base, expected_pairs, fix_number=True):
        """
        Read entries in uploaded ZIP.
        Raise Exception in case pairs HDR/IMG are not matched or number "expected_pairs" is not met.
        :returns: string with HDR list (to be passed to DTI pipeline).
        """
        
        hdr_files = []
        for file_name in zip_arch.namelist():
            if not file_name.startswith(file_name_base) or file_name.endswith("/"):
                continue
            if file_name.endswith(".hdr"):
                pair_img = file_name.replace(".hdr", ".img")
                if pair_img not in zip_arch.namelist():
                    raise ConnectException("Could not find pair for HDR file :" + str(file_name))
                
                new_file_name = os.path.join(result_folder, file_name_base + str(len(hdr_files)) + ".hdr")
                src = zip_arch.open(file_name, 'rU')
                FilesHelper.copy_file(src, new_file_name)
                hdr_files.append(os.path.join(remote_prefix, os.path.split(new_file_name)[1]))
                new_file_name = new_file_name.replace(".hdr", ".img")
                src = zip_arch.open(pair_img, 'rU')
                FilesHelper.copy_file(src, new_file_name)
                
            elif not file_name.endswith(".img"):
                self.logger.warning("Ignored file :" + str(file_name))
            
        if len(hdr_files) < expected_pairs or (fix_number and len(hdr_files) > expected_pairs):
            raise ConnectException("Invalid number of files:" + str(len(hdr_files)) +
                                   " expected:" + str(expected_pairs))

        result = ""
        for hdr_name in hdr_files:
            result = result + hdr_name + " "
        return result


    def _gather_results(self, current_user, current_project, result_matrix1, result_matrix2, 
                        temp_output_folder, zip_output):
        """
        Gather results, and launch final operation
        """
        ### Gather resulting files
        self.file_handler.unpack_zip(self.default_connectivity_zip_path, temp_output_folder)
        result_matrix1 = self._copy_file_from_remote(result_matrix1, temp_output_folder)
        result_matrix2 = self._copy_file_from_remote(result_matrix2, temp_output_folder)
        self._process_csv_file(result_matrix1, self.WEIGHTS_FILE)
        self._process_csv_file(result_matrix2, self.TRACT_FILE)
        ### Pack all results in a single ZIP file
        zip_output = self.file_handler.zip_folder(zip_output, temp_output_folder)
        
        ### Run Connectivity importer from ZIP
        group = self.flow_service.get_algorithm_by_module_and_class(self.CONNECTIVITY_IMPORTER[0], 
                                                                    self.CONNECTIVITY_IMPORTER[1])[1]
        adapter_instance = self.flow_service.build_adapter_instance(group)
        self.flow_service.fire_operation(adapter_instance, current_user, current_project.id, uploaded=zip_output)
                    
                                                               
     
    def fire_pipeline(self, dti_scans, current_project, current_user, number_of_threads=1):
        """
        Fire Pipeline execution as a distinct thread.
        """
        thread.start_new(self._internal_pipeline_thread, (dti_scans, current_project, current_user, number_of_threads))
        
        
    def _internal_pipeline_thread(self, dti_scans, current_project, current_user, number_of_th=1):
        """
        Actual Fire Pipeline execution remotely.
        """
        ### Prepare file-names
        uq_identifier = "TVB_" + str(utils.generate_guid())
        temp_input_folder = os.path.join(TVBSettings.TVB_TEMP_FOLDER, "IN_PIPELINE_" + uq_identifier)
        temp_output_folder = os.path.join(TVBSettings.TVB_TEMP_FOLDER, "OUT_PIPELINE_" + uq_identifier)
        zip_output = os.path.join(TVBSettings.TVB_TEMP_FOLDER, "Connectivity" + uq_identifier + ".zip")
        
        remote_input_folder = "/home/" + self.remote_user + "/processing/INPUT_" + uq_identifier + os.path.sep
        remote_output_folder = "/home/" + self.remote_user + "/processing/" + uq_identifier
        result_matrix1 = os.path.join(remote_output_folder, uq_identifier + self.REMOTE_WEIGHTS_FILE)
        result_matrix2 = os.path.join(remote_output_folder, uq_identifier + self.REMOTE_TRACT_FILE)
        
        self._execute_remote("rm -R -f " + remote_input_folder)
        self._execute_remote("mkdir " + remote_input_folder)
        self._execute_remote("rm -R -f " + remote_output_folder)
        
        ### Prepare and Copy required Input Files on the DTI remote machine.
        os.mkdir(temp_input_folder)
        prefix_files = os.path.split(os.path.dirname(remote_input_folder))[1]
        
        zip_arch = zipfile.ZipFile(dti_scans)
        dti_scans = self._process_input_zip(zip_arch, temp_input_folder, prefix_files, "Scans", 1, False)
        dti_ev = self._process_input_zip(zip_arch, temp_input_folder, prefix_files, "EigenVectors", 3)
        dti_fa = self._process_input_zip(zip_arch, temp_input_folder, prefix_files, "FA", 1)
        dti_md = self._process_input_zip(zip_arch, temp_input_folder, prefix_files, "MD", 1)
        dti_seg = self._process_input_zip(zip_arch, temp_input_folder, prefix_files, "Seg2DTI", 1)
        for local_name in os.listdir(temp_input_folder):
            self._copy_file_remote(os.path.join(temp_input_folder, local_name), 
                                   os.path.join(remote_input_folder, local_name))
            
        ### Execute remote DTI Pipeline command.
        dti_ev = dti_ev.split(' ')
        remote_command = self.DTI_PIPELINE_COMMAND % (os.path.split(remote_output_folder)[1], dti_seg, dti_ev[0], 
                                                      dti_ev[1], dti_ev[2], dti_scans, dti_fa, dti_md, number_of_th)
        self._execute_remote(remote_command)
        
        self._gather_results(current_user, current_project, result_matrix1, result_matrix2, 
                             temp_output_folder, zip_output)
        ### Clean left-over files
        self.file_handler.remove_folder(temp_output_folder)
        self.file_handler.remove_folder(temp_input_folder)
        os.remove(zip_output)
        self._execute_remote("rm -R -f " + remote_input_folder)
        self._execute_remote("rm -R -f " + remote_output_folder)

