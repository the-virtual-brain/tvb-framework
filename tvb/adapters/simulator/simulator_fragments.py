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

from tvb.core.entities.filters.chain import FilterChain
from tvb.datatypes.cortex import Cortex
from tvb.simulator.simulator import Simulator
from tvb.adapters.simulator.integrator_forms import get_ui_name_to_integrator_dict
from tvb.adapters.simulator.model_forms import get_ui_name_to_model
from tvb.adapters.simulator.monitor_forms import get_ui_name_to_monitor_dict
from tvb.core.adapters.abcadapter import ABCAdapterForm
from tvb.core.entities.model.datatypes.local_connectivity import LocalConnectivityIndex
from tvb.core.entities.model.datatypes.patterns import StimuliSurfaceIndex, StimuliRegionIndex
from tvb.core.entities.model.datatypes.region_mapping import RegionMappingIndex
from tvb.core.entities.model.datatypes.surface import SurfaceIndex
from tvb.core.neotraits._forms import DataTypeSelectField, SimpleSelectField, ScalarField, ArrayField


class SimulatorSurfaceFragment(ABCAdapterForm):
    def __init__(self, prefix='', project_id=None):
        super(SimulatorSurfaceFragment, self).__init__(prefix, project_id)
        # TODO: should show only corticals
        self.surface = DataTypeSelectField(SurfaceIndex, self, name='surface', required=False,
                                           label=Simulator.surface.label, doc=Simulator.surface.doc)


class SimulatorRMFragment(ABCAdapterForm):
    def __init__(self, prefix='', project_id=None, surface_index=None):
        super(SimulatorRMFragment, self).__init__(prefix, project_id)
        conditions = None
        if surface_index:
            conditions = FilterChain(fields=[FilterChain.datatype + '.surface_id'], operations=["=="],
                                     values=[surface_index.id])
        self.rm = DataTypeSelectField(RegionMappingIndex, self, name='region_mapping', required=True,
                                      label=Cortex.region_mapping_data.label,
                                      doc=Cortex.region_mapping_data.doc, conditions=conditions)
        self.lc = DataTypeSelectField(LocalConnectivityIndex, self, name='local_connectivity',
                                      label=Cortex.local_connectivity.label, doc=Cortex.local_connectivity.doc,
                                      conditions=conditions)
        self.coupling_strength = ArrayField(Cortex.coupling_strength, self)


class SimulatorStimulusFragment(ABCAdapterForm):
    def __init__(self, prefix='', project_id=None, is_surface_simulation=False):
        super(SimulatorStimulusFragment, self).__init__(prefix, project_id)
        if is_surface_simulation:
            stimuli_index_class = StimuliSurfaceIndex
        else:
            stimuli_index_class = StimuliRegionIndex
        self.stimulus = DataTypeSelectField(stimuli_index_class, self, name='region_stimuli', required=False,
                                            label=Simulator.stimulus.label, doc=Simulator.stimulus.doc)


class SimulatorModelFragment(ABCAdapterForm):
    def __init__(self, prefix='', project_id=None):
        super(SimulatorModelFragment, self).__init__(prefix, project_id)

        self.model_choices = get_ui_name_to_model()

        self.model = SimpleSelectField(choices=self.model_choices, form=self, name='model', required=True,
                                       label=Simulator.model.label, doc=Simulator.model.doc)
        self.model.template = "select_field.jinja2"


class SimulatorIntegratorFragment(ABCAdapterForm):

    def __init__(self, prefix='', project_id=None):
        super(SimulatorIntegratorFragment, self).__init__(prefix, project_id)

        self.integrator_choices = get_ui_name_to_integrator_dict()

        self.integrator = SimpleSelectField(choices=self.integrator_choices, form=self, name='integrator',
                                            required=True,
                                            label=Simulator.integrator.label, doc=Simulator.integrator.doc)
        self.integrator.template = "select_field.jinja2"


class SimulatorMonitorFragment(ABCAdapterForm):

    def __init__(self, prefix='', project_id=None):
        super(SimulatorMonitorFragment, self).__init__(prefix, project_id)

        self.monitor_choices = get_ui_name_to_monitor_dict()

        self.monitor = SimpleSelectField(choices=self.monitor_choices, form=self, name='monitor', required=True,
                                         label=Simulator.monitors.label, doc=Simulator.monitors.doc)
        self.monitor.template = "select_field.jinja2"


class SimulatorLengthFragment(ABCAdapterForm):

    def __init__(self, prefix='', project_id=None):
        super(SimulatorLengthFragment, self).__init__(prefix, project_id)
        self.length = ScalarField(Simulator.simulation_length, self)
        # TODO: name should be optional and auto-generated
        # self.simulation_name = SimpleStrField(self, 'simuation_name', required=True)
