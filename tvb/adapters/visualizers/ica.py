# -*-coding: utf-8 -*-

"""
A matrix displayer for the Independent Component Analysis.
It displays the mixing matrix of siae n_features x n_components

.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

import json
from tvb.datatypes.mode_decompositions import IndependentComponents
from tvb.core.adapters.abcdisplayer import ABCDisplayer
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)



class ICA(ABCDisplayer):
    _ui_name = "Independent Components Analysis"


    def get_input_tree(self):
        """Inform caller of the data we need"""

        return [{"name": "ica",
                 "type": IndependentComponents,
                 "label": "Independent component analysis:",
                 "required": True
                 }]


    def get_required_memory_size(self, **kwargs):
        "Return required memory. Here, it's unknown/insignificant."
        return -1


    def launch(self, ica):
        """Construct data for visualization and launch it."""

        # get data from IndependentComponents datatype, convert to json
        # HACK: dump only a 2D array
        matrix = abs(ica.get_data('mixing_matrix')[:, :, 0, 0])
        matrix_data = self.dump_prec(matrix.flat)
        matrix_shape = json.dumps(matrix.shape)
        matrix_strides = json.dumps(map(lambda x: x / matrix.itemsize, matrix.strides))

        view_pars = dict(matrix_data=matrix_data, matrix_shape=matrix_shape, matrix_strides=matrix_strides)

        return self.build_display_result("ica/view", view_pars)


    def generate_preview(self, ica, figure_size):
        return self.launch(ica)


    def dump_prec(self, xs, prec=3):
        """
        Dump a list of numbers into a string, each at the specified precision. 
        """

        return "[" + ",".join(map(lambda x: ("%0." + str(prec) + "g") % (x,), xs)) + "]"

