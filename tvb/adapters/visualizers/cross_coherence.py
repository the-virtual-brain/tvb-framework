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
A displayer for the cross coherence of a time series.

.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import json
from tvb.datatypes.spectral import CoherenceSpectrum
from tvb.core.adapters.abcdisplayer import ABCDisplayer



class CrossCoherenceVisualizer(ABCDisplayer):
    _ui_name = "Cross coherence visualizer"
    _ui_subsection = "coherence"


    def get_input_tree(self):
        """Inform caller of the data we need"""

        return [{"name": "coherence_spectrum",
                 "type": CoherenceSpectrum,
                 "label": "Coherence spectrum:",
                 "required": True
                 }]


    def get_required_memory_size(self, **kwargs):
        """Return required memory. Here, it's unknown/insignificant."""
        return -1


    def launch(self, coherence_spectrum):
        """Construct data for visualization and launch it."""

        # get data from coher datatype, convert to json
        frequency = self.dump_prec(coherence_spectrum.get_data('frequency').flat)

        # js needs to know shape and stride, not just elements
        array_data = coherence_spectrum.get_data('array_data')
        coherence = self.dump_prec(coherence_spectrum.get_data('array_data').flat)  # may be a long string
        shape = json.dumps(array_data.shape)
        strides = json.dumps(map(lambda x: x / array_data.itemsize, array_data.strides))

        return self.build_display_result("cross_coherence/view",
                                         dict(frequency=frequency, coherence=coherence, shape=shape, strides=strides))


    def generate_preview(self, coherence_spectrum, figure_size):
        return self.launch(coherence_spectrum)


    def dump_prec(self, xs, prec=3):
        """
        Dump a list of numbers into a string, each at the specified precision. 
        """

        return "[" + ",".join(map(lambda x: ("%0." + str(prec) + "g") % (x,), xs)) + "]"

