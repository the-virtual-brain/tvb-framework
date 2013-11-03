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
A displayer for cross correlation.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import json
import numpy
from tvb.datatypes.graph import CorrelationCoefficients
from tvb.datatypes.temporal_correlations import CrossCorrelation
from tvb.core.adapters.abcdisplayer import ABCDisplayer



class CrossCorrelationVisualizer(ABCDisplayer):
    _ui_name = "Cross correlation"
    _ui_subsection = "correlation"


    def get_input_tree(self):
        """Inform caller of the data we need as input """

        return [{"name": "cross_correlation", "type": CrossCorrelation,
                 "label": "Cross correlation", "required": True}]


    def get_required_memory_size(self, cross_correlation):
        """Return required memory. Here, it's unknown/insignificant."""
        input_size = cross_correlation.read_data_shape()
        return numpy.prod(input_size) / input_size[0] * 8.0


    def launch(self, cross_correlation):
        """Construct data for visualization and launch it."""

        matrix = cross_correlation.get_data('array_data').mean(axis=0)[:, :, 0, 0]
        return self._mainDisplay(matrix)


    def generate_preview(self, cross_correlation, figure_size):
        return self.launch(cross_correlation)


    def _mainDisplay(self, matrix):
        """
        Prepare JSON matrix for display
        :param matrix: input 2D matrix
        :return: Genshi template
        """
        matrix_data = self._dump_prec(matrix.flat)
        matrix_shape = json.dumps(matrix.shape)
        matrix_strides = json.dumps(map(lambda x: x / matrix.itemsize, matrix.strides))

        view_pars = dict(matrix_data=matrix_data, matrix_shape=matrix_shape, matrix_strides=matrix_strides)
        return self.build_display_result("cross_correlation/view", view_pars)


    def _dump_prec(self, xs, prec=3):
        """ Dump a list of numbers into a string, each at the specified precision. """

        return "[" + ",".join(map(lambda x: ("%0." + str(prec) + "g") % (x,), xs)) + "]"



class PearsonCorrelationCoefficientVisualizer(CrossCorrelationVisualizer):
    """
    Viewer for Pearson CorrelationCoefficients.
    Very similar to the CrossCorrelationVisualizer
    """
    _ui_name = "Cross Correlation Coefficients"
    _ui_subsection = "correlation_pearson"


    def get_input_tree(self):
        """ Inform caller of the data we need as input """

        return [{"name": "cross_correlation", "type": CorrelationCoefficients,
                 "label": "Correlation Coefficients", "required": True}]


    def get_required_memory_size(self, cross_correlation):
        """Return required memory."""

        input_size = cross_correlation.read_data_shape()
        return numpy.prod(input_size) * 8.0


    def launch(self, cross_correlation):
        """Construct data for visualization and launch it."""

        # Currently only the first mode & state-var are displayed.
        # TODO: display other mode / state-var
        matrix = cross_correlation.get_data('array_data')[:, :, 0, 0]
        return self._mainDisplay(matrix)

