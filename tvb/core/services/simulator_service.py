import copy
import json
import uuid
import os
from tvb.basic.logger.builder import get_logger
from tvb.datatypes.connectivity import Connectivity
from tvb.simulator.simulator import Simulator
from tvb.core.entities.file.datatypes.connectivity_h5 import ConnectivityH5
from tvb.core.entities.file.files_helper import FilesHelper
from tvb.core.entities.file.simulator.simulator_h5 import SimulatorH5
from tvb.core.entities.model.model_datatype import DataTypeGroup
from tvb.core.entities.model.model_operation import Operation
from tvb.core.entities.model.simulator.simulator import SimulatorIndex
from tvb.core.entities.storage import dao, transactional
from tvb.core.entities.transient.structure_entities import DataTypeMetaData
from tvb.core.services.burst_service2 import BurstService2
from tvb.core.services.operation_service import OperationService
from tvb.core.neocom.h5 import DirLoader


class SimulatorService(object):
    MAX_BURSTS_DISPLAYED = 50
    LAUNCH_NEW = 'new'
    LAUNCH_BRANCH = 'branch'

    def __init__(self):
        self.logger = get_logger(self.__class__.__module__)
        self.operation_service = OperationService()
        self.files_helper = FilesHelper()

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


    def _set_simulator_range_parameter(self, simulator, range_parameter_name, range_parameter_value):
        range_param_name_list = range_parameter_name.split('.')
        current_attr = simulator
        for param_name in range_param_name_list[:len(range_param_name_list) - 1]:
            current_attr = getattr(current_attr, param_name)
        setattr(current_attr, range_param_name_list[-1], range_parameter_value)

    def async_launch_and_prepare(self, burst_config, user, project, simulator_algo, range_param1, range_param2,
                                 session_stored_simulator):
        try:
            simulator_id = simulator_algo.id
            algo_category = simulator_algo.algorithm_category
            simulator_index = burst_config.simulator
            operation_group = burst_config.operation_group
            metric_operation_group = burst_config.metric_operation_group
            operations = []
            range_param2_values = []
            if range_param2:
                range_param2_values = range_param2.get_range_values()
            for param1_value in range_param1.get_range_values():
                for param2_value in range_param2_values:
                    simulator = copy.deepcopy(session_stored_simulator)
                    self._set_simulator_range_parameter(simulator, range_param1.name, param1_value)
                    self._set_simulator_range_parameter(simulator, range_param2.name, param2_value)

                    operation = self._prepare_operation(burst_config.id, project.id, user.id, simulator_id,
                                                        simulator_index, algo_category, operation_group)

                    simulator_index.fk_from_operation = operation.id
                    dao.store_entity(simulator_index)

                    storage_path = self.files_helper.get_project_folder(project, str(operation.id))
                    self.serialize_simulator(simulator, simulator_index.gid, storage_path)
                    operations.append(operation)

                    # TODO: will create an extra SimulatorIndex. Keep SimIndex?
                    simulator_index = SimulatorIndex()
                    simulator_index = dao.store_entity(simulator_index)

            first_operation = operations[0]
            datatype_group = DataTypeGroup(operation_group, operation_id=first_operation.id,
                                           fk_parent_burst=burst_config.id,
                                           state=json.loads(first_operation.meta_data)[DataTypeMetaData.KEY_STATE])
            dao.store_entity(datatype_group)

            metrics_datatype_group = DataTypeGroup(metric_operation_group, fk_parent_burst=burst_config.id)
            dao.store_entity(metrics_datatype_group)

            wf_errs = 0
            for operation in operations:
                try:
                    OperationService().launch_operation(operation.id, True)
                except Exception as excep:
                    self.logger.error(excep)
                    wf_errs += 1
                    BurstService2().mark_burst_finished(burst_config, error_message=str(excep))

            self.logger.debug("Finished launching workflows. " + str(len(operations) - wf_errs) +
                              " were launched successfully, " + str(wf_errs) + " had error on pre-launch steps")

        except Exception as excep:
            self.logger.error(excep)
            BurstService2().mark_burst_finished(burst_config, error_message=str(excep))
