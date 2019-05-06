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
Adapter that uses the traits module to generate interfaces for FFT Analyzer.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>

"""
import os
import uuid
import numpy
from tvb.analyzers.node_coherence import NodeCoherence
from tvb.core.adapters.abcadapter import ABCAsynchronous, ABCAdapterForm
from tvb.datatypes.time_series import TimeSeries
from tvb.datatypes.spectral import CoherenceSpectrum
from tvb.basic.filters.chain import FilterChain
from tvb.basic.logger.builder import get_logger

from tvb.core.entities.file.datatypes.spectral_h5 import CoherenceSpectrumH5
from tvb.core.entities.file.datatypes.time_series import TimeSeriesH5
from tvb.core.entities.model.datatypes.spectral import CoherenceSpectrumIndex
from tvb.core.entities.model.datatypes.time_series import TimeSeriesIndex
from tvb.core.neotraits._forms import ScalarField, DataTypeSelectField
from tvb.interfaces.neocom._h5loader import DirLoader

LOG = get_logger(__name__)

class NodeCoherenceForm(ABCAdapterForm):

    def __init__(self, prefix='', project_id=None):
        super(NodeCoherenceForm, self).__init__(prefix)
        self.time_series = DataTypeSelectField(NodeCoherence.time_series, self.get_required_datatype(), self,
                                               conditions=self.get_filters())
        self.nfft = ScalarField(NodeCoherence.nfft, self)
        self.project_id = project_id

    @staticmethod
    def get_required_datatype():
        return TimeSeriesIndex

    @staticmethod
    def get_filters():
        return FilterChain(fields=[FilterChain.datatype + '.data_ndim'], operations=["=="], values=[4])

    @staticmethod
    def get_input_name():
        return "time_series"

    def get_traited_datatype(self):
        return NodeCoherence()


class NodeCoherenceAdapter(ABCAsynchronous):
    """ TVB adapter for calling the NodeCoherence algorithm. """

    _ui_name = "Cross coherence of nodes"
    _ui_description = "Compute Node Coherence for a TimeSeries input DataType."
    _ui_subsection = "coherence"

    form = None

    def get_input_tree(self):
        return None

    def get_form(self):
        if self.form is None:
            return NodeCoherenceForm
        return self.form

    def set_form(self, form):
        self.form = form

    def get_output(self):
        return [CoherenceSpectrum]


    def configure(self, time_series, nfft=None):
        """
        Store the input shape to be later used to estimate memory usage.
        Also create the algorithm instance.
        """
        self.input_time_series_index = time_series
        self.input_shape = (self.input_time_series_index.data_length_1d,
                            self.input_time_series_index.data_length_2d,
                            self.input_time_series_index.data_length_3d,
                            self.input_time_series_index.data_length_4d)
        LOG.debug("Time series shape is %s" % str(self.input_shape))
        ##-------------------- Fill Algorithm for Analysis -------------------##
        self.algorithm = NodeCoherence()
        if nfft is not None:
            self.algorithm.nfft = nfft


    def get_required_memory_size(self, time_series, nfft=None):
        """
        Return the required memory to run this algorithm.
        """
        used_shape = (self.input_shape[0],
                      1,
                      self.input_shape[2],
                      self.input_shape[3])
        input_size = numpy.prod(used_shape) * 8.0
        output_size = self.algorithm.result_size(used_shape)
        return input_size + output_size


    def get_required_disk_size(self, time_series, nfft=None):
        """
        Returns the required disk size to be able to run the adapter (in kB).
        """
        used_shape = (self.input_shape[0],
                      1,
                      self.input_shape[2],
                      self.input_shape[3])
        return self.array_size2kb(self.algorithm.result_size(used_shape))


    def launch(self, time_series, nfft=None):
        """ 
        Launch algorithm and build results. 
        """
        ##--------- Prepare a CoherenceSpectrum object for result ------------##
        coherence_spectrum_index = CoherenceSpectrumIndex()

        loader = DirLoader(os.path.join(os.path.dirname(self.storage_path), str(self.input_time_series_index.fk_from_operation)))
        input_path = loader.path_for(TimeSeriesH5, self.input_time_series_index.gid)
        time_series_h5 = TimeSeriesH5(path=input_path)

        loader = DirLoader(self.storage_path)
        dest_path = loader.path_for(CoherenceSpectrumH5, coherence_spectrum_index.gid)
        coherence_h5 = CoherenceSpectrumH5(dest_path)
        coherence_h5.gid.store(uuid.UUID(coherence_spectrum_index.gid))
        coherence_h5.source.store(time_series_h5.gid.load())
        coherence_h5.nfft.store(self.algorithm.nfft)

        ##------------- NOTE: Assumes 4D, Simulator timeSeries. --------------##
        input_shape = time_series_h5.data.shape
        node_slice = [slice(input_shape[0]), None, slice(input_shape[2]), slice(input_shape[3])]

        ##---------- Iterate over slices and compose final result ------------##
        small_ts = TimeSeries()
        small_ts.sample_rate = time_series_h5.sample_rate.load()
        partial_coh = None
        for var in range(input_shape[1]):
            node_slice[1] = slice(var, var + 1)
            small_ts.data = time_series_h5.read_data_slice(tuple(node_slice))
            self.algorithm.time_series = small_ts
            partial_coh = self.algorithm.evaluate()
            coherence_h5.write_data_slice(partial_coh)
        coherence_h5.frequency.store(partial_coh.frequency)
        coherence_h5.close()
        time_series_h5.close()

        coherence_spectrum_index.source = self.input_time_series_index
        coherence_spectrum_index.nfft = partial_coh.nfft
        coherence_spectrum_index.frequencies = partial_coh.frequency

        return coherence_spectrum_index


