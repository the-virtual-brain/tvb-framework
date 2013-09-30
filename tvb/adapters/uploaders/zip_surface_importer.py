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
.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""

import numpy
from tvb.core.adapters.abcadapter import ABCSynchronous
from tvb.core.entities.file.files_helper import FilesHelper
from tvb.datatypes.surfaces import Surface, CorticalSurface, SkinAir, BrainSkull, SkullSkin, EEGCap, FaceSurface
from tvb.datatypes.surfaces_data import CORTICAL, OUTER_SKIN, OUTER_SKULL, INNER_SKULL, EEG_CAP, FACE
from tvb.core.adapters.exceptions import LaunchException
from tvb.basic.logger.builder import get_logger



class ZIPSurfaceImporter(ABCSynchronous):
    """
    Handler for uploading a Surface Data archive, with files holding 
    vertices, normals and triangles to represent a surface data.
    """

    _ui_name = "Surface ZIP"
    _ui_subsection = "zip_surface_importer"
    _ui_description = "Import a Surface from ZIP"
    
    VERTICES_TOKEN = "vertices"
    NORMALS_TOKEN = "normals"
    TRIANGLES_TOKEN = "triangles"
        
    def __init__(self):
        ABCSynchronous.__init__(self)
        self.logger = get_logger(self.__class__.__module__)


    def get_input_tree(self):
        """ Take as input a ZIP archive. """
        return [{'name': 'uploaded', 'type': 'upload', 'required_type': 'application/zip',
                 'label': 'Surface file (zip)', 'required': True},
                {'name': 'surface_type', 'type': 'select', 'label': 'Surface type', 'required': True,
                 'options': [{'name': 'Cortical Surface', 'value': CORTICAL},
                             {'name': 'Brain Skull', 'value': INNER_SKULL},
                             {'name': 'Skull Skin', 'value': OUTER_SKULL},
                             {'name': 'Skin Air', 'value': OUTER_SKIN},
                             {'name': 'EEG Cap', 'value': EEG_CAP},
                             {'name': 'Face Surface', 'value': FACE}]},
                {'name': 'zero_based_triangles', 'label': 'Zero based triangles', 'type': 'bool', 'default': True}]
        
        
    def get_output(self):
        return [Surface]


    def get_required_memory_size(self, **kwargs):
        """
        Return the required memory to run this algorithm.
        As it is an upload algorithm and we do not have information about data, we can not approximate this.
        """
        return -1    

    def get_required_disk_size(self, **kwargs):
        """
        Returns the required disk size to be able to run the adapter.
        """
        return 0

    def launch(self, uploaded, surface_type, zero_based_triangles=False):
        """
        Execute import operations: unpack ZIP and build Surface object as result.

        :param uploaded: an archive containing the Surface data to be imported
        :param surface_type: a string from the following\: \
                            "Skin Air", "Skull Skin", "Brain Skull", "Cortical Surface", "EEG Cap", "Face"

        :returns: a subclass of `Surface` DataType
        :raises LaunchException: when
                * `uploaded` is missing
                * `surface_type` is invalid
        :raises RuntimeError: when triangles contain an invalid vertex index
        """
        if uploaded is None:
            raise LaunchException("Please select ZIP file which contains data to import")
  
        self.logger.debug("Start to import surface: '%s' from file: %s" % (surface_type, uploaded))
        try:
            files = FilesHelper().unpack_zip(uploaded, self.storage_path)
        except IOError:
            exception_str = "Did not find the specified ZIP at %s" % uploaded
            raise LaunchException(exception_str)
        
        vertices = []
        normals = []
        triangles = []
        for file_name in files:
            if file_name.lower().find(self.VERTICES_TOKEN) >= 0:
                vertices.append(file_name)            
                continue
            if file_name.lower().find(self.NORMALS_TOKEN) >= 0:
                normals.append(file_name)            
                continue
            if file_name.lower().find(self.TRIANGLES_TOKEN) >= 0:
                triangles.append(file_name)
                
        # Now detect and instantiate correct surface type
        self.logger.debug("Create surface instance")
        if surface_type == CORTICAL:
            surface = CorticalSurface()
        elif surface_type == INNER_SKULL:
            surface = BrainSkull()
        elif surface_type == OUTER_SKULL:
            surface = SkullSkin()
        elif surface_type == OUTER_SKIN:
            surface = SkinAir()
        elif surface_type == EEG_CAP:
            surface = EEGCap()
        elif surface_type == FACE:
            surface = FaceSurface()
        else:
            exception_str = "Could not determine surface type (selected option %s)" % surface_type
            raise LaunchException(exception_str)
            
        surface.storage_path = self.storage_path

        all_vertices, all_normals, all_triangles = self._process_files(vertices, normals, triangles)
        FilesHelper.remove_files(files, True)
        surface.zero_based_triangles = zero_based_triangles
        surface.vertices = all_vertices
        surface.vertex_normals = all_normals
        if zero_based_triangles:
            surface.triangles = all_triangles
        else:
            surface.triangles = all_triangles - 1
        surface.triangle_normals = None

        # Now check if the triangles of the surface are valid   
        triangles_min_vertex = numpy.amin(surface.triangles)
        if triangles_min_vertex < 0:
            if triangles_min_vertex == -1 and not zero_based_triangles:
                raise RuntimeError("Triangles contain a negative vertex index. Maybe you have a ZERO based surface.")
            else:
                raise RuntimeError("Your triangles contain a negative vertex index: %d" % triangles_min_vertex)
        
        no_of_vertices = len(surface.vertices)        
        triangles_max_vertex = numpy.amax(surface.triangles)
        if triangles_max_vertex >= no_of_vertices:
            if triangles_max_vertex == no_of_vertices and zero_based_triangles:
                raise RuntimeError("Your triangles contain an invalid vertex index: %d. \
                Maybe your surface is NOT ZERO Based." % triangles_max_vertex)
            else:
                raise RuntimeError("Your triangles contain an invalid vertex index: %d." % triangles_max_vertex)
            
        self.logger.debug("Surface ready to be stored")
        return surface


    @staticmethod
    def _process_files(list_of_vertices, list_of_normals, list_of_triangles):
        """
        Read vertices, normals and triangles from files.
        """
        if len(list_of_vertices) != len(list_of_normals) != len(list_of_triangles):
            raise Exception("The number of vertices files should be equal to the normals/triangles files.")
        vertices = []
        normals = []
        triangles = []
        vertices_files_lengths = []
    
        for idx, vertice in enumerate(list_of_vertices):
            current_vertices = numpy.loadtxt(vertice, dtype=numpy.float32)
            current_normals = numpy.loadtxt(list_of_normals[idx], dtype=numpy.float32)
            vertices_files_lengths.append(len(current_vertices))
            vertices.extend(current_vertices)
            normals.extend(current_normals)
    
        increment_value = 0
        for i, triangle in enumerate(list_of_triangles):
            current_triangles = numpy.loadtxt(triangle, dtype=numpy.int32)
            if not i:
                triangles.extend(current_triangles)
                continue
            increment_value = increment_value + vertices_files_lengths[i - 1]
            for j in xrange(len(current_triangles)):
                current_triangles[j] += increment_value
            triangles.extend(current_triangles)
    
        return (numpy.array(vertices, dtype=numpy.float64), 
                numpy.array(normals, dtype=numpy.float64), 
                numpy.array(triangles, dtype=numpy.int64))

