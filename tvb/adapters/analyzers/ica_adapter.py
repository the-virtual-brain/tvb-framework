# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and 
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
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
Adapter that uses the traits module to generate interfaces for ICA Analyzer.

.. moduleauthor:: Paula Sanz Leon

"""

import uuid
import numpy
from tvb.analyzers.ica import fastICA
from tvb.core.adapters.abcadapter import ABCAsynchronous
from tvb.datatypes.time_series import TimeSeries
from tvb.datatypes.mode_decompositions import IndependentComponents
from tvb.basic.filters.chain import FilterChain
from tvb.basic.logger.builder import get_logger

from tvb.core.entities.file.datatypes.mode_decompositions_h5 import IndependentComponentsH5
from tvb.core.entities.file.datatypes.time_series import TimeSeriesH5
from tvb.core.entities.model.datatypes.mode_decompositions import IndependentComponentsIndex
from tvb.interfaces.neocom._h5loader import DirLoader

LOG = get_logger(__name__)


class ICAAdapter(ABCAsynchronous):
    """ TVB adapter for calling the ICA algorithm. """

    _ui_name = "Independent Component Analysis"
    _ui_description = "ICA for a TimeSeries input DataType."
    _ui_subsection = "ica"

    def get_input_tree(self):
        """
        Return a list of lists describing the interface to the analyzer. This
        is used by the GUI to generate the menus and fields necessary for defining a simulation.
        """
        algorithm = fastICA()
        algorithm.trait.bound = self.INTERFACE_ATTRIBUTES_ONLY
        tree = algorithm.interface[self.INTERFACE_ATTRIBUTES]
        for node in tree:
            if node['name'] == 'time_series':
                node['conditions'] = FilterChain(fields=[FilterChain.datatype + '._nr_dimensions'],
                                                 operations=["=="], values=[4])
        return tree

    def get_output(self):
        return [IndependentComponents]

    def configure(self, time_series, n_components=None):
        """
        Store the input shape to be later used to estimate memory usage. Also
        create the algorithm instance.
        """
        self.input_time_series_index = time_series
        self.input_shape = (self.input_time_series_index.data.length_1d,
                            self.input_time_series_index.data.length_2d,
                            self.input_time_series_index.data.length_3d,
                            self.input_time_series_index.data.length_4d)
        LOG.debug("Time series shape is %s" % str(self.input_shape))
        LOG.debug("Provided number of components is %s" % n_components)
        ##-------------------- Fill Algorithm for Analysis -------------------##

        algorithm = fastICA()
        if n_components is not None:
            algorithm.n_components = n_components
        else:
            ## It will only work for Simulator results.
            algorithm.n_components = self.input_time_series_index.data.length_3d
        self.algorithm = algorithm

    def get_required_memory_size(self):
        """
        Return the required memory to run this algorithm.
        """
        used_shape = (self.input_shape[0], 1, self.input_shape[2], self.input_shape[3])
        input_size = numpy.prod(used_shape) * 8.0
        output_size = self.algorithm.result_size(self.input_shape)
        return input_size + output_size

    def get_required_disk_size(self):
        """
        Returns the required disk size to be able to run the adapter (in kB).
        """
        used_shape = (self.input_shape[0], 1, self.input_shape[2], self.input_shape[3])
        return self.array_size2kb(self.algorithm.result_size(used_shape))

    def launch(self):
        """ 
        Launch algorithm and build results. 
        """
        ##--------- Prepare a IndependentComponents object for result ----------##
        ica_index = IndependentComponentsIndex()
        gid = uuid.uuid4()
        ica_index.gid = gid
        ica_index.source = self.input_time_series_index

        loader = DirLoader(self.storage_path)
        input_path = loader.path_for(TimeSeriesH5, self.input_time_series_index.gid)
        time_series_h5 = TimeSeriesH5(path=input_path)

        result_path = loader.path_for(IndependentComponentsH5, gid)
        ica_h5 = IndependentComponentsH5(path=result_path)
        ica_h5.source = time_series_h5.gid.load()
        ica_h5.n_components = self.algorithm.n_components

        ##------------- NOTE: Assumes 4D, Simulator timeSeries. --------------##
        input_shape = time_series_h5.data.shape
        node_slice = [slice(input_shape[0]), None, slice(input_shape[2]), slice(input_shape[3])]

        ##---------- Iterate over slices and compose final result ------------##
        small_ts = TimeSeries()
        for var in range(input_shape[1]):
            node_slice[1] = slice(var, var + 1)
            small_ts.data = time_series_h5.read_data_slice(tuple(node_slice))
            self.algorithm.time_series = small_ts
            partial_ica = self.algorithm.evaluate()
            ica_h5.write_data_slice(partial_ica)
        ica_h5.close()

        return ica_index
