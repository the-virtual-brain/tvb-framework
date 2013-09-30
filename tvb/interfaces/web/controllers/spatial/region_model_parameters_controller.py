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
import tvb.interfaces.web.controllers.base_controller as base
from tvb.interfaces.web.controllers.users_controller import logged
from tvb.interfaces.web.controllers.base_controller import using_template, ajax_call
from tvb.interfaces.web.entities.context_model_parameters import ContextModelParameters
from tvb.interfaces.web.controllers.spatial.base_spatio_temporal_controller import SpatioTemporalController
from tvb.interfaces.web.controllers.spatial.base_spatio_temporal_controller import PARAMS_MODEL_PATTERN


### SESSION KEY for ContextModelParameter entity.
KEY_CONTEXT_MPR = "ContextForModelParametersOnRegion"


class RegionsModelParametersController(SpatioTemporalController):
    """
    Controller class for editing Model Parameters on regions in a visual manner.
    """
    
    def __init__(self):
        SpatioTemporalController.__init__(self)


    @cherrypy.expose
    @using_template('base_template')
    @logged()
    def edit_model_parameters(self):
        """
        Main method, to initialize Model-Parameter visual-set.
        """
        model, integrator, connectivity, _ = self.get_data_from_burst_configuration()

        connectivity_viewer_params = self.get_connectivity_parameters(connectivity)
        context_model_parameters = ContextModelParameters(connectivity, model, integrator)
        data_for_param_sliders = self.get_data_for_param_sliders('0', context_model_parameters)
        base.add2session(KEY_CONTEXT_MPR, context_model_parameters)

        template_specification = dict(title="Spatio temporal - Model parameters")
        template_specification['submit_parameters_url'] = '/spatial/modelparameters/regions/submit_model_parameters'
        template_specification['parametersNames'] = context_model_parameters.model_parameter_names
        template_specification['isSingleMode'] = True
        template_specification['paramSlidersData'] = json.dumps(data_for_param_sliders)
        template_specification.update(connectivity_viewer_params)
        template_specification['mainContent'] = 'spatial/model_param_region_main'
        template_specification['displayDefaultSubmitBtn'] = True
        template_specification.update(context_model_parameters.phase_plane_params)
        return self.fill_default_attributes(template_specification)


    @cherrypy.expose
    @using_template('spatial/model_param_region_param_sliders')
    @logged()
    def load_model_for_connectivity_node(self, connectivity_node_index):
        """
        Loads the model of the given connectivity node into the phase plane.
        """
        if int(connectivity_node_index) < 0:
            return
        context_model_parameters = base.get_from_session(KEY_CONTEXT_MPR)
        context_model_parameters.load_model_for_connectivity_node(connectivity_node_index)

        data_for_param_sliders = self.get_data_for_param_sliders(connectivity_node_index, context_model_parameters)
        template_specification = dict()
        template_specification['paramSlidersData'] = json.dumps(data_for_param_sliders)
        template_specification['parametersNames'] = data_for_param_sliders['all_param_names']
        return template_specification


    @cherrypy.expose
    @ajax_call()
    @logged()
    def update_model_parameter_for_nodes(self, param_name, new_param_value, connectivity_node_indexes):
        """
        Updates the specified model parameter for the first node from the 'connectivity_node_indexes'
        list and after that replace the model of each node from the 'connectivity_node_indexes' list
        with the model of the first node from the list.
        """
        connectivity_node_indexes = json.loads(connectivity_node_indexes)
        if not len(connectivity_node_indexes):
            return
        context_model_parameters = base.get_from_session(KEY_CONTEXT_MPR)
        first_node_index = connectivity_node_indexes[0]
        context_model_parameters.update_model_parameter(first_node_index, param_name, new_param_value)
        if len(connectivity_node_indexes) > 1:
            #eliminate the first node
            connectivity_node_indexes = connectivity_node_indexes[1: len(connectivity_node_indexes)]
            context_model_parameters.set_model_for_connectivity_nodes(first_node_index, connectivity_node_indexes)
        base.add2session(KEY_CONTEXT_MPR, context_model_parameters)


    @cherrypy.expose
    @ajax_call()
    @logged()
    def copy_model(self, from_node, to_nodes):
        """
        Replace the model of the nodes 'to_nodes' with the model of the node 'from_node'.

        ``from_node``: the index of the node from where will be copied the model
        ``to_nodes``: a list with the nodes indexes for which will be replaced the model
        """
        from_node = int(from_node)
        to_nodes = json.loads(to_nodes)
        if from_node < 0 or not len(to_nodes):
            return
        context_model_parameters = base.get_from_session(KEY_CONTEXT_MPR)
        context_model_parameters.set_model_for_connectivity_nodes(from_node, to_nodes)
        base.add2session(KEY_CONTEXT_MPR, context_model_parameters)


    @cherrypy.expose
    @using_template('spatial/model_param_region_param_sliders')
    @logged()
    def reset_model_parameters_for_nodes(self, connectivity_node_indexes):
        """
        Resets the model parameters, of the specified connectivity nodes, to their default values.
        """
        connectivity_node_indexes = json.loads(connectivity_node_indexes)
        if not len(connectivity_node_indexes):
            return

        context_model_parameters = base.get_from_session(KEY_CONTEXT_MPR)
        context_model_parameters.reset_model_parameters_for_nodes(connectivity_node_indexes)
        context_model_parameters.load_model_for_connectivity_node(connectivity_node_indexes[0])
        data_for_param_sliders = self.get_data_for_param_sliders(connectivity_node_indexes[0], context_model_parameters)
        base.add2session(KEY_CONTEXT_MPR, context_model_parameters)

        template_specification = dict()
        template_specification['paramSlidersData'] = json.dumps(data_for_param_sliders)
        template_specification['parametersNames'] = data_for_param_sliders['all_param_names']
        return template_specification


    @cherrypy.expose
    @ajax_call()
    @logged()
    def submit_model_parameters(self):
        """
        Collects the model parameters values from all the models used for the connectivity nodes.
        """
        context_model_parameters = base.get_from_session(KEY_CONTEXT_MPR)
        burst_configuration = base.get_from_session(base.KEY_BURST_CONFIG)
        for param_name in context_model_parameters.model_parameter_names:
            full_name = PARAMS_MODEL_PATTERN % (context_model_parameters.model_name, param_name)
            full_values = context_model_parameters.get_values_for_parameter(param_name)
            burst_configuration.update_simulation_parameter(full_name, full_values) 
        ### Clean from session drawing context
        base.remove_from_session(KEY_CONTEXT_MPR)
        ### Update in session BURST configuration for burst-page. 
        base.add2session(base.KEY_BURST_CONFIG, burst_configuration.clone())
        raise cherrypy.HTTPRedirect("/burst/")

        
    def fill_default_attributes(self, template_dictionary):
        """
        Overwrite base controller to add required parameters for adapter templates.
        """
        template_dictionary[base.KEY_SECTION] = 'burst'
        template_dictionary[base.KEY_SUB_SECTION] = 'regionmodel'
        template_dictionary[base.KEY_INCLUDE_RESOURCES] = 'spatial/included_resources'
        base.BaseController.fill_default_attributes(self, template_dictionary)
        return template_dictionary
    
