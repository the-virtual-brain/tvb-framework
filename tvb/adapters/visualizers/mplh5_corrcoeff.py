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
.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""
import numpy
from tvb.core.adapters.abcdisplayer import ABCMPLH5Displayer
from tvb.datatypes.graph import CorrelationCoefficients
from tvb.simulator.plot.tools import plot_tri_matrix


class PearsonCorrelationCoefficientVisualizer(ABCMPLH5Displayer):
    """
    Viewer for Pearson CorrelationCoefficients.
    Very similar to the CrossCorrelationVisualizer
    """
    _ui_name = "Pearson Correlation Coefficients"
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
        # TODO: display other modes / sv
        self.matrix       = cross_correlation.get_data('array_data')[:, :, 0, 0]
        ts_dtype          = cross_correlation.get_date('source')
        
        # I'm not sure this is going to work 
        self.node_labels = None
        if hasattr(ts_dtype, 'connectivity')
            self.node_labels = ts_dtype.connectivity.region_labels

        self.plot()


    def plot(self, figure, **kwargs):
        self.figure = figure
        self.axes.clear()
        self.figure = plot_tri_matrix(self.matrix, node_labels=self.node_labels)
        self.figure.canvas.draw()

#EoF#