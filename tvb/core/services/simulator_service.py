import json
import uuid
from tvb.simulator.simulator import Simulator
from tvb.core.entities.file.simulator.simulator_h5 import SimulatorH5
from tvb.core.entities.model.model_operation import Operation
from tvb.core.entities.storage import dao
from tvb.interfaces.neocom._h5loader import DirLoader


class SimulatorService(object):

    def serialize_simulator(self, simulator, simulator_gid, storage_path):
        dir_loader = DirLoader(storage_path)

        simulator_path = dir_loader.path_for_has_traits(type(simulator), simulator_gid)

        with SimulatorH5(simulator_path) as simulator_h5:
            simulator_h5.gid.store(uuid.UUID(simulator_gid))
            simulator_h5.store(simulator)
            simulator_h5.connectivity.store(simulator.connectivity.gid)

        return simulator_gid

    def deserialize_simulator(self, simulator_gid, storage_path):
        dir_loader = DirLoader(storage_path)

        simulator_in_path = dir_loader.path_for_has_traits(Simulator, simulator_gid)
        simulator_in = Simulator()

        with SimulatorH5(simulator_in_path) as simulator_in_h5:
            simulator_in_h5.load_into(simulator_in)
            connectivity_gid = simulator_in_h5.connectivity.load()

        return simulator_in, connectivity_gid

    def _prepare_operation(self, project_id, user_id, simulator_id, simulator_index):
        operation_parameters = json.dumps({'simulator_gid': simulator_index.gid})
        operation = Operation(user_id, project_id, simulator_id, operation_parameters)
        operation = dao.store_entity(operation)

        # TODO: prepare portlets/handle operation groups/no workflows

        return operation
