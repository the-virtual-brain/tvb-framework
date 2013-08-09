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
"""
import os
from nibabel.nifti1 import intent_codes, data_type_codes
import nibabel.gifti.giftiio as giftiio
from tvb.core.adapters.exceptions import ParseException
from tvb.basic.logger.builder import get_logger
from tvb.datatypes.surfaces import CorticalSurface, SkinAir
from tvb.datatypes.time_series import TimeSeriesSurface



class GIFTIParser():
    """
        This class reads content of a GIFTI file and builds / returns a Surface instance 
        filled with details.
    """
    UNIQUE_ID_ATTR = "UniqueID"
    SUBJECT_ATTR = "SubjectID"
    ASP_ATTR = "AnatomicalStructurePrimary"
    DATE_ATTR = "Date"
    DESCRIPTION_ATTR = "Description"
    NAME_ATTR = "Name"
    TIME_STEP_ATTR = "TimeStep"
    
    def __init__(self, storage_path, operation_id):
        self.logger = get_logger(__name__)
        self.storage_path = storage_path
        self.operation_id = operation_id
        
    def parse(self, data_file):
        """
            Parse NIFTI file and returns TimeSeries for it. 
        """
        self.logger.debug("Start to parse GIFTI file: %s"%data_file)
        if data_file is None:
            raise ParseException ("Please select GIFTI file which contains data to import")
        if not os.path.exists(data_file):
            raise ParseException ("Provided file %s does not exists"%data_file)
        try:
            gifti_image = giftiio.read(data_file)
            self.logger.debug("File parsed successfully")
        except Exception, excep:
            self.logger.exception(excep)
            msg = "File: %s does not have a valid GIFTI format." % data_file
            raise ParseException(msg)
        
        
        # Now try to determine what data is stored in GIFTI file
        data_arrays = gifti_image.darrays
        
        self.logger.debug("Determine data type stored in GIFTI file")
        
        # First check if it's a surface
        if (len(data_arrays) == 2 
            and intent_codes.code["NIFTI_INTENT_POINTSET"] == data_arrays[0].intent
            and data_type_codes.code["NIFTI_TYPE_FLOAT32"] == data_arrays[0].datatype
            and intent_codes.code["NIFTI_INTENT_TRIANGLE"] == data_arrays[1].intent
            and data_type_codes.code["NIFTI_TYPE_INT32"] == data_arrays[1].datatype):
            
            # Now try to determine what type of surface we have
            data_array_meta = data_arrays[0].meta
            surface = None
            gid = None
            subject = None
            title = None
            
            if (data_array_meta is not None and data_array_meta.data is not None 
                   and len(data_array_meta.data) > 0):
                anatomical_structure_primary = None
                
                for meta_pair in data_array_meta.data:
                    if meta_pair.name == self.ASP_ATTR:
                        anatomical_structure_primary = meta_pair.value
                    elif meta_pair.name == self.UNIQUE_ID_ATTR:
                        gid = meta_pair.value.replace("{", "").replace("}", "")
                    elif meta_pair.name == self.SUBJECT_ATTR:
                        subject = meta_pair.value
                    elif meta_pair.name == self.NAME_ATTR:
                        title = meta_pair.value
                        
                # Based on info found in meta create correct surface type
                if anatomical_structure_primary == "Head":
                    surface = SkinAir()
                elif anatomical_structure_primary.startswith("Cortex"):
                    surface = CorticalSurface()
                
            
            if surface is None:
                raise ParseException("Could not determine type of the surface")
            
            # Now fill TVB data type with info
            if gid is not None:
                surface.gid = gid
            
            surface.storage_path = self.storage_path
            surface.set_operation_id(self.operation_id)
            
            surface.zero_based_triangles = True
            surface.vertices = data_arrays[0].data
            surface.triangles = data_arrays[1].data
            
            if subject is not None:
                surface.subject = subject
            if title is not None:
                surface.title = title
            
            return surface
        
        elif(len(data_arrays) > 1 
            and intent_codes.code["NIFTI_INTENT_TIME_SERIES"] == data_arrays[0].intent
            and data_type_codes.code["NIFTI_TYPE_FLOAT32"] == data_arrays[0].datatype):
            
            # Create TVB time series to be filled
            time_series = TimeSeriesSurface()
            time_series.storage_path = self.storage_path
            time_series.set_operation_id(self.operation_id)
            time_series.start_time = 0.0
            time_series.sample_period = 1.0

            # First process first data_array and extract important data from it's metadata            
            data_array_meta = data_arrays[0].meta
            if (data_array_meta is not None and data_array_meta.data is not None 
                   and len(data_array_meta.data) > 0):
                for meta_pair in data_array_meta.data:
                    if meta_pair.name == self.UNIQUE_ID_ATTR:
                        gid = meta_pair.value.replace("{", "").replace("}", "")
                        if gid is not None and len(gid) > 0:
                            time_series.gid = gid
                    elif meta_pair.name == self.SUBJECT_ATTR:
                        time_series.subject = meta_pair.value
                    elif meta_pair.name == self.NAME_ATTR:
                        time_series.title = meta_pair.value
                    elif meta_pair.name == self.TIME_STEP_ATTR:
                        time_series.sample_period = float(meta_pair.value)
            
            
            # Now read time series data
            for data_array in data_arrays:
                time_series.write_data_slice([data_array.data])
            
            # Close file after writing data
            time_series.close_file()
            
            return time_series
        else:
            raise ParseException("Could not map data from GIFTI file to a TVB data type")