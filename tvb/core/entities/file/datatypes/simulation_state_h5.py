from tvb.core.neotraits.h5 import H5File, DataSet, Scalar
from tvb.datatypes.simulation_state import SimulationState


class SimulationStateH5(H5File):

    def __init__(self, path):
        super(SimulationStateH5, self).__init__(path)
        self.history = DataSet(SimulationState.history)
        self.current_state = DataSet(SimulationState.current_state)
        self.current_step = Scalar(SimulationState.current_step)
        self.monitor_stock_1 = DataSet(SimulationState.monitor_stock_1)
        self.monitor_stock_2 = DataSet(SimulationState.monitor_stock_2)
        self.monitor_stock_3 = DataSet(SimulationState.monitor_stock_3)
        self.monitor_stock_4 = DataSet(SimulationState.monitor_stock_4)
        self.monitor_stock_5 = DataSet(SimulationState.monitor_stock_5)
        self.monitor_stock_6 = DataSet(SimulationState.monitor_stock_6)
        self.monitor_stock_7 = DataSet(SimulationState.monitor_stock_7)
        self.monitor_stock_8 = DataSet(SimulationState.monitor_stock_8)
        self.monitor_stock_9 = DataSet(SimulationState.monitor_stock_9)
        self.monitor_stock_10 = DataSet(SimulationState.monitor_stock_10)
        self.monitor_stock_11 = DataSet(SimulationState.monitor_stock_11)
        self.monitor_stock_12 = DataSet(SimulationState.monitor_stock_12)
        self.monitor_stock_13 = DataSet(SimulationState.monitor_stock_13)
        self.monitor_stock_14 = DataSet(SimulationState.monitor_stock_14)
        self.monitor_stock_15 = DataSet(SimulationState.monitor_stock_15)

        self._end_accessor_declarations()
