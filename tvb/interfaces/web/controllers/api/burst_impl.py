
"""
Reloadable module of functions that implements burst API.

This is separated in order to speed development 

"""

import json 

import tvb.interfaces.web.controllers.basecontroller as base

"""
model_parameters_option_Generic2dOscillator_state_variable_range_parameters_W
integrator
surface
integrator_parameters_option_HeunDeterministic_dt
simulation_length
monitors_parameters_option_TemporalAverage_period
monitors
conduction_speed
model_parameters_option_Generic2dOscillator_a
model_parameters_option_Generic2dOscillator_b
model_parameters_option_Generic2dOscillator_c
model_parameters_option_Generic2dOscillator_tau
model_parameters_option_Generic2dOscillator_noise
model_parameters_option_Generic2dOscillator_noise_parameters_option_Noise_random_stream_parameters_option_RandomStream_init_seed
connectivity
model_parameters_option_Generic2dOscillator_noise_parameters_option_Noise_random_stream
range_1
range_2
coupling_parameters_option_Linear_b
model_parameters_option_Generic2dOscillator_noise_parameters_option_Noise_ntau
coupling_parameters_option_Linear_a
model_parameters_option_Generic2dOscillator_state_variable_range_parameters_V
coupling
model_parameters_option_Generic2dOscillator_I
stimulus
currentAlgoId
model_parameters_option_Generic2dOscillator_variables_of_interest
model
"""

class HierStruct(object):
    """
    Class to handle by flat and nested indexing of simulator configuration


    """

    pass


def index(self):
    return 'Burst API'

def read(self, pid):
    pid = int(pid)
    info = {}
    bursts = self.burst_service.get_available_bursts(pid)
    import pdb; pdb.set_trace()
    for burst in bursts:
        info[burst.name] = {k:v for k,v in burst.simulator_configuration.iteritems() if len(k)>0}
    return json.dumps(info)


def create(self, opt):
    # NotImplemented
    return 'NotImplemented'

