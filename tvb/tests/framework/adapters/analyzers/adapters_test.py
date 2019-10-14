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

import os
from tvb.adapters.analyzers.ica_adapter import ICAAdapter
from tvb.adapters.analyzers.metrics_group_timeseries import TimeseriesMetricsAdapter
from tvb.adapters.analyzers.pca_adapter import PCAAdapter
from tvb.adapters.analyzers.wavelet_adapter import ContinuousWaveletTransformAdapter
from tvb.core.entities.file.datatypes.mapped_value_h5 import DatatypeMeasureH5
from tvb.core.entities.file.datatypes.mode_decompositions_h5 import PrincipalComponentsH5, IndependentComponentsH5
from tvb.core.entities.file.datatypes.spectral_h5 import WaveletCoefficientsH5
from tvb.core.neocom import h5
from tvb.tests.framework.adapters.analyzers.fft_test import make_ts_from_op


def test_wavelet_adapter(tmpdir, session, operationFactory):
    storage_folder = str(tmpdir)
    ts_index = make_ts_from_op(session, operationFactory)

    wavelet_adapter = ContinuousWaveletTransformAdapter()
    wavelet_adapter.storage_path = storage_folder
    wavelet_adapter.configure(ts_index)

    diskq = wavelet_adapter.get_required_disk_size()
    memq = wavelet_adapter.get_required_memory_size()

    wavelet_idx = wavelet_adapter.launch(ts_index)

    result_h5 = h5.path_for(storage_folder, WaveletCoefficientsH5, wavelet_idx.gid)
    assert os.path.exists(result_h5)


def test_pca_adapter(tmpdir, session, operationFactory):
    storage_folder = str(tmpdir)
    ts_index = make_ts_from_op(session, operationFactory)

    pca_adapter = PCAAdapter()
    pca_adapter.storage_path = storage_folder
    pca_adapter.configure(ts_index)

    disk = pca_adapter.get_required_disk_size(ts_index)
    mem = pca_adapter.get_required_memory_size(ts_index)

    pca_idx = pca_adapter.launch(ts_index)

    result_h5 = h5.path_for(storage_folder, PrincipalComponentsH5, pca_idx.gid)
    assert os.path.exists(result_h5)


def test_ica_adapter(tmpdir, session, operationFactory):
    storage_folder = str(tmpdir)
    ts_index = make_ts_from_op(session, operationFactory)

    ica_adapter = ICAAdapter()
    ica_adapter.storage_path = storage_folder
    ica_adapter.configure(ts_index)

    disk = ica_adapter.get_required_disk_size(ts_index)
    mem = ica_adapter.get_required_memory_size(ts_index)

    ica_idx = ica_adapter.launch(ts_index)

    result_h5 = h5.path_for(storage_folder, IndependentComponentsH5, ica_idx.gid)
    assert os.path.exists(result_h5)


def test_metrics_adapter_launch(tmpdir, session, operationFactory):
    storage_folder = str(tmpdir)
    ts_index = make_ts_from_op(session, operationFactory)

    metrics_adapter = TimeseriesMetricsAdapter()
    metrics_adapter.storage_path = storage_folder
    metrics_adapter.configure(ts_index)

    disk = metrics_adapter.get_required_disk_size()
    mem = metrics_adapter.get_required_memory_size()

    datatype_measure_index = metrics_adapter.launch(ts_index)

    result_h5 = h5.path_for(storage_folder, DatatypeMeasureH5, datatype_measure_index.gid)
    assert  os.path.exists(result_h5)