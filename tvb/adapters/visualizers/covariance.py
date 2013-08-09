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
A displayer for covariance.

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import json
from tvb.datatypes.graph import Covariance
from tvb.core.adapters.abcdisplayer import ABCDisplayer



class CovarianceVisualizer(ABCDisplayer):
    _ui_name = "Covariance visualizer"


    def get_input_tree(self):
        """Inform caller of the data we need"""

        return [{"name": "covariance",
                 "type": Covariance,
                 "label": "Covariance",
                 "required": True
                 }]


    def get_required_memory_size(self, **kwargs):
        """Return required memory. Here, it's unknown/insignificant."""
        return -1


    def launch(self, covariance):
        """Construct data for visualization and launch it."""

        # get data from corr datatype, convert to json
        matrix = covariance.get_data('array_data')

        matrix_data = self.dump_prec(matrix.flat)
        matrix_shape = json.dumps(matrix.shape)
        matrix_strides = json.dumps(map(lambda x: x / matrix.itemsize, matrix.strides))

        view_pars = dict(matrix_data=matrix_data, matrix_shape=matrix_shape, matrix_strides=matrix_strides)
        return self.build_display_result("covariance/view", view_pars)


    def generate_preview(self, covariance, figure_size):
        return self.launch(covariance)


    def dump_prec(self, xs, prec=3):
        """
        Dump a list of numbers into a string, each at the specified precision. 
        """

        return "[" + ",".join(map(lambda x: ("%0." + str(prec) + "g") % (x,), xs)) + "]"

