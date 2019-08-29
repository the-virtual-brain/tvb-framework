import json

import numpy
from tvb.simulator.models import Epileptor, Epileptor2D, EpileptorCodim3, EpileptorCodim3SlowMod, Hopfield, JansenRit, \
    ZetterbergJansen, JC_Epileptor, LarterBreakspear, Linear, Generic2dOscillator, Kuramoto, ReducedSetFitzHughNagumo, \
    ReducedSetHindmarshRose, WilsonCowan, ReducedWongWang, ReducedWongWangExcIOInhI, Zerlaut_adaptation_first_order, \
    Zerlaut_adaptation_second_order
from tvb.simulator.models.oscillator import supHopf

from tvb.core.entities.file.simulator.configurations_h5 import SimulatorConfigurationH5
from tvb.core.neotraits._h5accessors import Json
from tvb.core.neotraits._h5core import DataSet


class StateVariablesEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, numpy.ndarray):
            o = o.tolist()
        return o


class StateVariablesDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_array)

    def dict_array(self, dictionary):
        dict_array = {}
        for k, v in dictionary.iteritems():
            dict_array.update({k: numpy.array(v)})
        return dict_array


class EpileptorH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(EpileptorH5, self).__init__(path, None)

        self.a = DataSet(Epileptor.a, self)
        self.b = DataSet(Epileptor.b, self)
        self.c = DataSet(Epileptor.c, self)
        self.d = DataSet(Epileptor.d, self)
        self.r = DataSet(Epileptor.r, self)
        self.s = DataSet(Epileptor.s, self)
        self.x0 = DataSet(Epileptor.x0, self)
        self.Iext = DataSet(Epileptor.Iext, self)
        self.slope = DataSet(Epileptor.slope, self)
        self.Iext2 = DataSet(Epileptor.Iext2, self)
        self.tau = DataSet(Epileptor.tau, self)
        self.aa = DataSet(Epileptor.aa, self)
        self.bb = DataSet(Epileptor.bb, self)
        self.Kvf = DataSet(Epileptor.Kvf, self)
        self.Kf = DataSet(Epileptor.Kf, self)
        self.Ks = DataSet(Epileptor.Ks, self)
        self.tt = DataSet(Epileptor.tt, self)
        self.modification = DataSet(Epileptor.modification, self)
        # TODO: check encoding/decoding here
        self.state_variable_range = Json(Epileptor.state_variable_range, self, json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # TODO: error regarding unicode at load time, should be fixed by py3
        # self.variables_of_interest = Json(Epileptor.variables_of_interest, self)


class Epileptor2DH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(Epileptor2DH5, self).__init__(path, None)

        self.a = DataSet(Epileptor2D.a, self)
        self.b = DataSet(Epileptor2D.b, self)
        self.c = DataSet(Epileptor2D.c, self)
        self.d = DataSet(Epileptor2D.d, self)
        self.r = DataSet(Epileptor2D.r, self)
        self.x0 = DataSet(Epileptor2D.x0, self)
        self.Iext = DataSet(Epileptor2D.Iext, self)
        self.slope = DataSet(Epileptor2D.slope, self)
        self.Kvf = DataSet(Epileptor2D.Kvf, self)
        self.Ks = DataSet(Epileptor2D.Ks, self)
        self.tt = DataSet(Epileptor2D.tt, self)
        self.modification = DataSet(Epileptor2D.modification, self)
        self.state_variable_range = Json(Epileptor2D.state_variable_range, self, json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(Epileptor2D.variables_of_interest, self)


class EpileptorCodim3H5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(EpileptorCodim3H5, self).__init__(path, None)
        self.mu1_start = DataSet(EpileptorCodim3.mu1_start, self)
        self.mu2_start = DataSet(EpileptorCodim3.mu2_start, self)
        self.nu_start = DataSet(EpileptorCodim3.nu_start, self)
        self.mu1_stop = DataSet(EpileptorCodim3.mu1_stop, self)
        self.mu2_stop = DataSet(EpileptorCodim3.mu2_stop, self)
        self.nu_stop = DataSet(EpileptorCodim3.nu_stop, self)
        self.b = DataSet(EpileptorCodim3.b, self)
        self.R = DataSet(EpileptorCodim3.R, self)
        self.c = DataSet(EpileptorCodim3.c, self)
        self.dstar = DataSet(EpileptorCodim3.dstar, self)
        self.Ks = DataSet(EpileptorCodim3.Ks, self)
        self.N = DataSet(EpileptorCodim3.N, self)
        self.modification = DataSet(EpileptorCodim3.modification, self)
        self.state_variable_range = Json(EpileptorCodim3.state_variable_range, self, json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(EpileptorCodim3.variables_of_interest, self)


class EpileptorCodim3SlowModH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(EpileptorCodim3SlowModH5, self).__init__(path, None)
        self.mu1_Ain = DataSet(EpileptorCodim3SlowMod.mu1_Ain, self)
        self.mu2_Ain = DataSet(EpileptorCodim3SlowMod.mu2_Ain, self)
        self.nu_Ain = DataSet(EpileptorCodim3SlowMod.nu_Ain, self)
        self.mu1_Bin = DataSet(EpileptorCodim3SlowMod.mu1_Bin, self)
        self.mu2_Bin = DataSet(EpileptorCodim3SlowMod.mu2_Bin, self)
        self.nu_Bin = DataSet(EpileptorCodim3SlowMod.nu_Bin, self)
        self.mu1_Aend = DataSet(EpileptorCodim3SlowMod.mu1_Aend, self)
        self.mu2_Aend = DataSet(EpileptorCodim3SlowMod.mu2_Aend, self)
        self.nu_Aend = DataSet(EpileptorCodim3SlowMod.nu_Aend, self)
        self.mu1_Bend = DataSet(EpileptorCodim3SlowMod.mu1_Bend, self)
        self.mu2_Bend = DataSet(EpileptorCodim3SlowMod.mu2_Bend, self)
        self.nu_Bend = DataSet(EpileptorCodim3SlowMod.nu_Bend, self)
        self.b = DataSet(EpileptorCodim3SlowMod.b, self)
        self.R = DataSet(EpileptorCodim3SlowMod.R, self)
        self.c = DataSet(EpileptorCodim3SlowMod.c, self)
        self.cA = DataSet(EpileptorCodim3SlowMod.cA, self)
        self.cB = DataSet(EpileptorCodim3SlowMod.cB, self)
        self.dstar = DataSet(EpileptorCodim3SlowMod.dstar, self)
        self.Ks = DataSet(EpileptorCodim3SlowMod.Ks, self)
        self.N = DataSet(EpileptorCodim3SlowMod.N, self)
        self.modification = DataSet(EpileptorCodim3SlowMod.modification, self)
        self.state_variable_range = Json(EpileptorCodim3SlowMod.state_variable_range, self,
                                         json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(EpileptorCodim3SlowMod.variables_of_interest, self)


class HopfieldH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(HopfieldH5, self).__init__(path, None)
        self.taux = DataSet(Hopfield.taux, self)
        self.tauT = DataSet(Hopfield.tauT, self)
        self.dynamic = DataSet(Hopfield.dynamic, self)
        self.state_variable_range = Json(Hopfield.state_variable_range, self, json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(Hopfield.variables_of_interest, self)


class JansenRitH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(JansenRitH5, self).__init__(path, None)
        self.A = DataSet(JansenRit.A, self)
        self.B = DataSet(JansenRit.B, self)
        self.a = DataSet(JansenRit.a, self)
        self.b = DataSet(JansenRit.b, self)
        self.v0 = DataSet(JansenRit.v0, self)
        self.nu_max = DataSet(JansenRit.nu_max, self)
        self.r = DataSet(JansenRit.r, self)
        self.J = DataSet(JansenRit.J, self)
        self.a_1 = DataSet(JansenRit.a_1, self)
        self.a_2 = DataSet(JansenRit.a_2, self)
        self.a_3 = DataSet(JansenRit.a_3, self)
        self.a_4 = DataSet(JansenRit.a_4, self)
        self.p_min = DataSet(JansenRit.p_min, self)
        self.p_max = DataSet(JansenRit.p_max, self)
        self.mu = DataSet(JansenRit.mu, self)
        self.state_variable_range = Json(JansenRit.state_variable_range, self, json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(JansenRit.variables_of_interest, self)


class ZetterbergJansenH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(ZetterbergJansenH5, self).__init__(path, None)
        self.He = DataSet(ZetterbergJansen.He, self)
        self.Hi = DataSet(ZetterbergJansen.Hi, self)
        self.ke = DataSet(ZetterbergJansen.ke, self)
        self.ki = DataSet(ZetterbergJansen.ki, self)
        self.e0 = DataSet(ZetterbergJansen.e0, self)
        self.rho_2 = DataSet(ZetterbergJansen.rho_2, self)
        self.rho_1 = DataSet(ZetterbergJansen.rho_1, self)
        self.gamma_1 = DataSet(ZetterbergJansen.gamma_1, self)
        self.gamma_2 = DataSet(ZetterbergJansen.gamma_2, self)
        self.gamma_3 = DataSet(ZetterbergJansen.gamma_3, self)
        self.gamma_4 = DataSet(ZetterbergJansen.gamma_4, self)
        self.gamma_5 = DataSet(ZetterbergJansen.gamma_5, self)
        self.gamma_1T = DataSet(ZetterbergJansen.gamma_1T, self)
        self.gamma_2T = DataSet(ZetterbergJansen.gamma_2T, self)
        self.gamma_3T = DataSet(ZetterbergJansen.gamma_3T, self)
        self.P = DataSet(ZetterbergJansen.P, self)
        self.U = DataSet(ZetterbergJansen.U, self)
        self.Q = DataSet(ZetterbergJansen.Q, self)
        self.state_variable_range = Json(ZetterbergJansen.state_variable_range, self,
                                         json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(ZetterbergJansen.variables_of_interest, self)


class JC_EpileptorH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(JC_EpileptorH5, self).__init__(path, None)
        self.a = DataSet(JC_Epileptor.a, self)
        self.b = DataSet(JC_Epileptor.b, self)
        self.c = DataSet(JC_Epileptor.c, self)
        self.d = DataSet(JC_Epileptor.d, self)
        self.r = DataSet(JC_Epileptor.r, self)
        self.s = DataSet(JC_Epileptor.s, self)
        self.x0 = DataSet(JC_Epileptor.x0, self)
        self.Iext = DataSet(JC_Epileptor.Iext, self)
        self.slope = DataSet(JC_Epileptor.slope, self)
        self.Iext2 = DataSet(JC_Epileptor.Iext2, self)
        self.tau = DataSet(JC_Epileptor.tau, self)
        self.aa = DataSet(JC_Epileptor.aa, self)
        self.bb = DataSet(JC_Epileptor.bb, self)
        self.Kvf = DataSet(JC_Epileptor.Kvf, self)
        self.Kf = DataSet(JC_Epileptor.Kf, self)
        self.Ks = DataSet(JC_Epileptor.Ks, self)
        self.tt = DataSet(JC_Epileptor.tt, self)
        self.tau_rs = DataSet(JC_Epileptor.tau_rs, self)
        self.I_rs = DataSet(JC_Epileptor.I_rs, self)
        self.a_rs = DataSet(JC_Epileptor.a_rs, self)
        self.b_rs = DataSet(JC_Epileptor.b_rs, self)
        self.d_rs = DataSet(JC_Epileptor.d_rs, self)
        self.e_rs = DataSet(JC_Epileptor.e_rs, self)
        self.f_rs = DataSet(JC_Epileptor.f_rs, self)
        self.alpha_rs = DataSet(JC_Epileptor.alpha_rs, self)
        self.beta_rs = DataSet(JC_Epileptor.beta_rs, self)
        self.gamma_rs = DataSet(JC_Epileptor.gamma_rs, self)
        self.K_rs = DataSet(JC_Epileptor.K_rs, self)
        self.p = DataSet(JC_Epileptor.p, self)
        self.state_variable_range = Json(JC_Epileptor.state_variable_range, self, json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(JC_Epileptor.variables_of_interest, self)


class LarterBreakspearH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(LarterBreakspearH5, self).__init__(path, None)
        self.gCa = DataSet(LarterBreakspear.gCa, self)
        self.gK = DataSet(LarterBreakspear.gK, self)
        self.gL = DataSet(LarterBreakspear.gL, self)
        self.phi = DataSet(LarterBreakspear.phi, self)
        self.gNa = DataSet(LarterBreakspear.gNa, self)
        self.TK = DataSet(LarterBreakspear.TK, self)
        self.TCa = DataSet(LarterBreakspear.TCa, self)
        self.TNa = DataSet(LarterBreakspear.TNa, self)
        self.VCa = DataSet(LarterBreakspear.VCa, self)
        self.VK = DataSet(LarterBreakspear.VK, self)
        self.VL = DataSet(LarterBreakspear.VL, self)
        self.VNa = DataSet(LarterBreakspear.VNa, self)
        self.d_K = DataSet(LarterBreakspear.d_K, self)
        self.tau_K = DataSet(LarterBreakspear.tau_K, self)
        self.d_Na = DataSet(LarterBreakspear.d_Na, self)
        self.d_Ca = DataSet(LarterBreakspear.d_Ca, self)
        self.aei = DataSet(LarterBreakspear.aei, self)
        self.aie = DataSet(LarterBreakspear.aie, self)
        self.b = DataSet(LarterBreakspear.b, self)
        self.C = DataSet(LarterBreakspear.C, self)
        self.ane = DataSet(LarterBreakspear.ane, self)
        self.ani = DataSet(LarterBreakspear.ani, self)
        self.aee = DataSet(LarterBreakspear.aee, self)
        self.Iext = DataSet(LarterBreakspear.Iext, self)
        self.rNMDA = DataSet(LarterBreakspear.rNMDA, self)
        self.VT = DataSet(LarterBreakspear.VT, self)
        self.d_V = DataSet(LarterBreakspear.d_V, self)
        self.ZT = DataSet(LarterBreakspear.ZT, self)
        self.d_Z = DataSet(LarterBreakspear.d_Z, self)
        self.QV_max = DataSet(LarterBreakspear.QV_max, self)
        self.QZ_max = DataSet(LarterBreakspear.QZ_max, self)
        self.t_scale = DataSet(LarterBreakspear.t_scale, self)
        # self.variables_of_interest = Json(LarterBreakspear.variables_of_interest, self)
        self.state_variable_range = Json(LarterBreakspear.state_variable_range, self,
                                         json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)


class LinearH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(LinearH5, self).__init__(path, None)
        self.gamma = DataSet(Linear.gamma, self)
        self.state_variable_range = Json(Linear.state_variable_range, self, json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(Linear.variables_of_interest, self)


class Generic2dOscillatorH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(Generic2dOscillatorH5, self).__init__(path, None)
        self.tau = DataSet(Generic2dOscillator.tau, self)
        self.I = DataSet(Generic2dOscillator.I, self)
        self.a = DataSet(Generic2dOscillator.a, self)
        self.b = DataSet(Generic2dOscillator.b, self)
        self.c = DataSet(Generic2dOscillator.c, self)
        self.d = DataSet(Generic2dOscillator.d, self)
        self.e = DataSet(Generic2dOscillator.e, self)
        self.f = DataSet(Generic2dOscillator.f, self)
        self.g = DataSet(Generic2dOscillator.g, self)
        self.alpha = DataSet(Generic2dOscillator.alpha, self)
        self.beta = DataSet(Generic2dOscillator.beta, self)
        self.gamma = DataSet(Generic2dOscillator.gamma, self)
        # TODO: handle Json.dumops for dict value
        self.state_variable_range = Json(Generic2dOscillator.state_variable_range, self,
                                         json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # TODO: issue with unicode at load time
        # self.variables_of_interest = Json(Generic2dOscillator.variables_of_interest, self)


class KuramotoH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(KuramotoH5, self).__init__(path, None)
        self.omega = DataSet(Kuramoto.omega, self)
        self.state_variable_range = Json(Kuramoto.state_variable_range, self, json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(Kuramoto.variables_of_interest, self)


class supHopfH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(supHopfH5, self).__init__(path, None)
        self.a = DataSet(supHopf.a, self)
        self.omega = DataSet(supHopf.omega, self)
        self.state_variable_range = Json(supHopf.state_variable_range, self, json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(supHopf.variables_of_interest, self)


class ReducedSetFitzHughNagumoH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(ReducedSetFitzHughNagumoH5, self).__init__(path, None)
        self.tau = DataSet(ReducedSetFitzHughNagumo.tau, self)
        self.a = DataSet(ReducedSetFitzHughNagumo.a, self)
        self.b = DataSet(ReducedSetFitzHughNagumo.b, self)
        self.K11 = DataSet(ReducedSetFitzHughNagumo.K11, self)
        self.K12 = DataSet(ReducedSetFitzHughNagumo.K12, self)
        self.K21 = DataSet(ReducedSetFitzHughNagumo.K21, self)
        self.sigma = DataSet(ReducedSetFitzHughNagumo.sigma, self)
        self.mu = DataSet(ReducedSetFitzHughNagumo.mu, self)
        self.state_variable_range = Json(ReducedSetFitzHughNagumo.state_variable_range, self,
                                         json_encoder=StateVariablesEncoder, json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(ReducedSetFitzHughNagumo.variables_of_interest, self)


class ReducedSetHindmarshRoseH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(ReducedSetHindmarshRoseH5, self).__init__(path, None)
        self.r = DataSet(ReducedSetHindmarshRose.r, self)
        self.a = DataSet(ReducedSetHindmarshRose.a, self)
        self.b = DataSet(ReducedSetHindmarshRose.b, self)
        self.c = DataSet(ReducedSetHindmarshRose.c, self)
        self.d = DataSet(ReducedSetHindmarshRose.d, self)
        self.s = DataSet(ReducedSetHindmarshRose.s, self)
        self.xo = DataSet(ReducedSetHindmarshRose.xo, self)
        self.K11 = DataSet(ReducedSetHindmarshRose.K11, self)
        self.K12 = DataSet(ReducedSetHindmarshRose.K12, self)
        self.K21 = DataSet(ReducedSetHindmarshRose.K21, self)
        self.sigma = DataSet(ReducedSetHindmarshRose.sigma, self)
        self.mu = DataSet(ReducedSetHindmarshRose.mu, self)
        self.state_variable_range = Json(ReducedSetHindmarshRose.state_variable_range, self,
                                         json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(ReducedSetHindmarshRose.variables_of_interest, self)


class WilsonCowanH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(WilsonCowanH5, self).__init__(path, None)
        self.c_ee = DataSet(WilsonCowan.c_ee, self)
        self.c_ie = DataSet(WilsonCowan.c_ie, self)
        self.c_ei = DataSet(WilsonCowan.c_ei, self)
        self.c_ii = DataSet(WilsonCowan.c_ii, self)
        self.tau_e = DataSet(WilsonCowan.tau_e, self)
        self.tau_i = DataSet(WilsonCowan.tau_i, self)
        self.a_e = DataSet(WilsonCowan.a_e, self)
        self.b_e = DataSet(WilsonCowan.b_e, self)
        self.c_e = DataSet(WilsonCowan.c_e, self)
        self.theta_e = DataSet(WilsonCowan.theta_e, self)
        self.a_i = DataSet(WilsonCowan.a_i, self)
        self.b_i = DataSet(WilsonCowan.b_i, self)
        self.theta_i = DataSet(WilsonCowan.theta_i, self)
        self.c_i = DataSet(WilsonCowan.c_i, self)
        self.r_e = DataSet(WilsonCowan.r_e, self)
        self.r_i = DataSet(WilsonCowan.r_i, self)
        self.k_e = DataSet(WilsonCowan.k_e, self)
        self.k_i = DataSet(WilsonCowan.k_i, self)
        self.P = DataSet(WilsonCowan.P, self)
        self.Q = DataSet(WilsonCowan.Q, self)
        self.alpha_e = DataSet(WilsonCowan.alpha_e, self)
        self.alpha_i = DataSet(WilsonCowan.alpha_i, self)
        self.state_variable_range = Json(WilsonCowan.state_variable_range, self, json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(WilsonCowan.variables_of_interest, self)


class ReducedWongWangH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(ReducedWongWangH5, self).__init__(path, None)
        self.a = DataSet(ReducedWongWang.a, self)
        self.b = DataSet(ReducedWongWang.b, self)
        self.d = DataSet(ReducedWongWang.d, self)
        self.gamma = DataSet(ReducedWongWang.gamma, self)
        self.tau_s = DataSet(ReducedWongWang.tau_s, self)
        self.w = DataSet(ReducedWongWang.w, self)
        self.J_N = DataSet(ReducedWongWang.J_N, self)
        self.I_o = DataSet(ReducedWongWang.I_o, self)
        self.sigma_noise = DataSet(ReducedWongWang.sigma_noise, self)
        self.state_variable_range = Json(ReducedWongWang.state_variable_range, self, json_encoder=StateVariablesEncoder,
                                         json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(ReducedWongWang.variables_of_interest, self)


class ReducedWongWangExcIOInhIH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(ReducedWongWangExcIOInhIH5, self).__init__(path, None)
        self.a_e = DataSet(ReducedWongWangExcIOInhI.a_e, self)
        self.b_e = DataSet(ReducedWongWangExcIOInhI.b_e, self)
        self.d_e = DataSet(ReducedWongWangExcIOInhI.d_e, self)
        self.gamma_e = DataSet(ReducedWongWangExcIOInhI.gamma_e, self)
        self.tau_e = DataSet(ReducedWongWangExcIOInhI.tau_e, self)
        self.w_p = DataSet(ReducedWongWangExcIOInhI.w_p, self)
        self.J_N = DataSet(ReducedWongWangExcIOInhI.J_N, self)
        self.W_e = DataSet(ReducedWongWangExcIOInhI.W_e, self)
        self.a_i = DataSet(ReducedWongWangExcIOInhI.a_i, self)
        self.b_i = DataSet(ReducedWongWangExcIOInhI.b_i, self)
        self.d_i = DataSet(ReducedWongWangExcIOInhI.d_i, self)
        self.gamma_i = DataSet(ReducedWongWangExcIOInhI.gamma_i, self)
        self.tau_i = DataSet(ReducedWongWangExcIOInhI.tau_i, self)
        self.J_i = DataSet(ReducedWongWangExcIOInhI.J_i, self)
        self.W_i = DataSet(ReducedWongWangExcIOInhI.W_i, self)
        self.I_o = DataSet(ReducedWongWangExcIOInhI.I_o, self)
        self.G = DataSet(ReducedWongWangExcIOInhI.G, self)
        self.lamda = DataSet(ReducedWongWangExcIOInhI.lamda, self)
        self.state_variable_range = Json(ReducedWongWangExcIOInhI.state_variable_range, self,
                                         json_encoder=StateVariablesEncoder, json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(ReducedWongWangExcIOInhI.variables_of_interest, self)


class Zerlaut_adaptation_first_orderH5(SimulatorConfigurationH5):

    def __init__(self, path):
        super(Zerlaut_adaptation_first_orderH5, self).__init__(path, None)
        self.g_L = DataSet(Zerlaut_adaptation_first_order.g_L, self)
        self.E_L_e = DataSet(Zerlaut_adaptation_first_order.E_L_e, self)
        self.E_L_i = DataSet(Zerlaut_adaptation_first_order.E_L_i, self)
        self.C_m = DataSet(Zerlaut_adaptation_first_order.C_m, self)
        self.b = DataSet(Zerlaut_adaptation_first_order.b, self)
        self.tau_w = DataSet(Zerlaut_adaptation_first_order.tau_w, self)
        self.E_e = DataSet(Zerlaut_adaptation_first_order.E_e, self)
        self.E_i = DataSet(Zerlaut_adaptation_first_order.E_i, self)
        self.Q_e = DataSet(Zerlaut_adaptation_first_order.Q_e, self)
        self.Q_i = DataSet(Zerlaut_adaptation_first_order.Q_i, self)
        self.tau_e = DataSet(Zerlaut_adaptation_first_order.tau_e, self)
        self.tau_i = DataSet(Zerlaut_adaptation_first_order.tau_i, self)
        self.N_tot = DataSet(Zerlaut_adaptation_first_order.N_tot, self)
        self.p_connect = DataSet(Zerlaut_adaptation_first_order.p_connect, self)
        self.g = DataSet(Zerlaut_adaptation_first_order.g, self)
        self.T = DataSet(Zerlaut_adaptation_first_order.T, self)
        self.P_e = DataSet(Zerlaut_adaptation_first_order.P_e, self)
        self.P_i = DataSet(Zerlaut_adaptation_first_order.P_i, self)
        self.external_input = DataSet(Zerlaut_adaptation_first_order.external_input, self)
        self.state_variable_range = Json(Zerlaut_adaptation_first_order.state_variable_range, self,
                                         json_encoder=StateVariablesEncoder, json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(Zerlaut_adaptation_first_order.variables_of_interest, self)


class Zerlaut_adaptation_second_orderH5(Zerlaut_adaptation_first_orderH5):

    def __init__(self, path):
        super(Zerlaut_adaptation_second_orderH5, self).__init__(path, None)
        self.state_variable_range = Json(Zerlaut_adaptation_second_order.state_variable_range, self,
                                         json_encoder=StateVariablesEncoder, json_decoder=StateVariablesDecoder)
        # self.variables_of_interest = Json(Zerlaut_adaptation_second_order.variables_of_interest, self)
