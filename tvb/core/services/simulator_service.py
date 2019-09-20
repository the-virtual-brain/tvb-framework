import json
import uuid
import os
from tvb.basic.logger.builder import get_logger
from tvb.datatypes.connectivity import Connectivity
from tvb.simulator.simulator import Simulator
from tvb.core.entities.file.datatypes.connectivity_h5 import ConnectivityH5
from tvb.core.entities.file.simulator.simulator_h5 import SimulatorH5
from tvb.core.entities.model.model_operation import Operation
from tvb.core.entities.storage import dao, transactional
from tvb.core.entities.transient.structure_entities import DataTypeMetaData
from tvb.core.services.operation_service import OperationService
from tvb.core.neocom.h5 import DirLoader


class SimulatorService(object):
    MAX_BURSTS_DISPLAYED = 50
    LAUNCH_NEW = 'new'
    LAUNCH_BRANCH = 'branch'

    def __init__(self):
        self.logger = get_logger(self.__class__.__module__)
        self.operation_service = OperationService()

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

        conn_index = dao.get_datatype_by_gid(connectivity_gid.hex)
        dir_loader = DirLoader(os.path.join(os.path.dirname(storage_path), str(conn_index.fk_from_operation)))

        conn_path = dir_loader.path_for(ConnectivityH5, connectivity_gid)
        conn = Connectivity()
        with ConnectivityH5(conn_path) as conn_h5:
            conn_h5.load_into(conn)

        simulator_in.connectivity = conn
        return simulator_in, connectivity_gid

    @transactional
    def _prepare_operation(self, burst_id, project_id, user_id, simulator_id, simulator_index, algo_category, op_group):
        operation_parameters = json.dumps({'simulator_gid': simulator_index.gid})
        metadata = {DataTypeMetaData.KEY_BURST: burst_id}
        metadata, user_group = self.operation_service._prepare_metadata(metadata, algo_category, op_group, {})
        meta_str = json.dumps(metadata)

        op_group_id = None
        if op_group:
            op_group_id = op_group.id

        operation = Operation(user_id, project_id, simulator_id, operation_parameters, op_group_id=op_group_id, meta=meta_str)

        self.logger.debug("Saving Operation(userId=" + str(user_id) + ",projectId=" + str(project_id) + "," +
                          str(metadata) + ",algorithmId=" + str(simulator_id) + ", ops_group= " + str(op_group_id) + ")")

        # visible_operation = visible and category.display is False
        operation = dao.store_entity(operation)
        # operation.visible = visible_operation

        # TODO: prepare portlets/handle operation groups/no workflows

        return operation
