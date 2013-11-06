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
.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
.. moduleauthor:: Ionel Ortelecan <ionel.ortelecan@codemart.ro>
"""

import json
import cherrypy
from tvb.config import SIMULATOR_MODULE, SIMULATOR_CLASS
from tvb.core.adapters.abcadapter import ABCAdapter
from tvb.core.services.flow_service import FlowService
import tvb.interfaces.web.controllers.base_controller as base
from tvb.interfaces.web.controllers.users_controller import logged
from tvb.interfaces.web.controllers.base_controller import using_template, ajax_call
from tvb.interfaces.web.entities.context_noise_configuration import ContextNoiseParameters
from tvb.interfaces.web.controllers.spatial.base_spatio_temporal_controller import SpatioTemporalController


### SESSION KEY for ContextModelParameter entity.
KEY_CONTEXT_NC = "ContextForModelParametersOnRegion"


class NoiseConfigurationController(SpatioTemporalController):
    """
    Controller class for editing Model Parameters on regions in a visual manner.
    """
    
    def __init__(self):
        SpatioTemporalController.__init__(self)


    @cherrypy.expose
    @using_template('base_template')
    @logged()
    def edit_noise_parameters(self):
        """
        Main method, to initialize Model-Parameter visual-set.
        """
        model, integrator, connectivity, _ = self.get_data_from_burst_configuration()

        connectivity_viewer_params = self.get_connectivity_parameters(connectivity)
        context_noise_config = ContextNoiseParameters(connectivity, model, integrator)
        param_names, param_data = self.get_data_for_param_sliders('0', context_noise_config)
        base.add2session(KEY_CONTEXT_NC, context_noise_config)

        template_specification = dict(title="Simulation - Noise configuration")
        template_specification['submit_parameters_url'] = '/spatial/noiseconfiguration/submit_noise_configuration'
        template_specification['parametersNames'] = param_names
        template_specification['paramSlidersData'] = param_data
        template_specification['isSingleMode'] = True
        template_specification.update(connectivity_viewer_params)
        template_specification['mainContent'] = 'spatial/noise_configuration_main'
        template_specification['displayDefaultSubmitBtn'] = True
        return self.fill_default_attributes(template_specification)
    
    
    @cherrypy.expose
    @ajax_call()
    @logged()
    def update_noise_configuration(self, **data):
        """
        Updates the specified model parameter for the first node from the 'connectivity_node_indexes'
        list and after that replace the model of each node from the 'connectivity_node_indexes' list
        with the model of the first node from the list.
        """
        noise_values = json.loads(data['noiseValues'])
        selected_regions = json.loads(data['selectedNodes'])
        context_noise_config = base.get_from_session(KEY_CONTEXT_NC)
        for node_idx in selected_regions:
            for model_param_idx in noise_values.keys():
                context_noise_config.update_noise_configuration(node_idx, model_param_idx,
                                                                noise_values[model_param_idx])


    @cherrypy.expose
    @ajax_call()
    @logged()
    def load_initial_values(self):
        """
        Returns a json with the current noise configuration.
        """
        context_noise_config = base.get_from_session(KEY_CONTEXT_NC)
        return context_noise_config.noise_values


    @cherrypy.expose
    @ajax_call()
    @logged()
    def load_noise_values_for_connectivity_node(self, connectivity_index):
        """
        Gets currently configured noise parameters for the specified connectivity node
        """
        connectivity_index = int(connectivity_index)
        context_noise_config = base.get_from_session(KEY_CONTEXT_NC)
        node_values = {}
        for idx in xrange(len(context_noise_config.noise_values)):
            node_values[idx] = context_noise_config.noise_values[idx][connectivity_index]
        return node_values


    @cherrypy.expose
    @ajax_call()
    @logged()
    def copy_configuration(self, from_node, to_nodes):
        """
        Loads a noise configuration from ``from_node`` and copies that to all
        nodes named in the ``to_nodes`` array
        :returns: noise values json array
        """
        from_node = int(from_node)
        to_nodes = json.loads(to_nodes)
        if from_node < 0 or not len(to_nodes):
            return
        context_model_parameters = base.get_from_session(KEY_CONTEXT_NC)
        context_model_parameters.set_noise_connectivity_nodes(from_node, to_nodes)
        base.add2session(KEY_CONTEXT_NC, context_model_parameters)
        return context_model_parameters.noise_values

    @cherrypy.expose
    @ajax_call()
    @logged()
    def submit_noise_configuration(self):
        """
        Collects the model parameters values from all the models used for the connectivity nodes.
        """
        context_noise_config = base.get_from_session(KEY_CONTEXT_NC)
        burst_configuration = base.get_from_session(base.KEY_BURST_CONFIG)
        _, simulator_group = FlowService().get_algorithm_by_module_and_class(SIMULATOR_MODULE, SIMULATOR_CLASS)
        simulator_adapter = ABCAdapter.build_adapter(simulator_group)
        for param_name in simulator_adapter.noise_configurable_parameters():
            burst_configuration.update_simulation_parameter(param_name, str(context_noise_config.noise_values)) 
        ### Clean from session drawing context
        base.remove_from_session(KEY_CONTEXT_NC)
        ### Update in session BURST configuration for burst-page. 
        base.add2session(base.KEY_BURST_CONFIG, burst_configuration.clone())
        raise cherrypy.HTTPRedirect("/burst/")

        
    def fill_default_attributes(self, template_dictionary):
        """
        Overwrite base controller to add required parameters for adapter templates.
        """
        template_dictionary[base.KEY_SECTION] = 'burst'
        template_dictionary[base.KEY_SUB_SECTION] = 'noiseconfig'
        template_dictionary[base.KEY_INCLUDE_RESOURCES] = 'spatial/included_resources'
        base.BaseController.fill_default_attributes(self, template_dictionary)
        return template_dictionary

