from datetime import datetime
from tvb.basic.logger.builder import get_logger
from tvb.core.entities.file.files_helper import FilesHelper
from tvb.core.entities.model.model_datatype import DataTypeGroup
from tvb.core.entities.model.simulator.burst_configuration import BurstConfiguration2
from tvb.core.entities.storage import dao


class BurstService2(object):

    def __init__(self):
        self.logger = get_logger(self.__class__.__module__)
        self.file_helper = FilesHelper()

    def mark_burst_finished(self, burst_entity, burst_status=None, error_message=None):
        """
        Mark Burst status field.
        Also compute 'weight' for current burst: no of operations inside, estimate time on disk...

        :param burst_entity: BurstConfiguration to be updated, at finish time.
        :param burst_status: BurstConfiguration status. By default BURST_FINISHED
        :param error_message: If given, set the status to error and perpetuate the message.
        """
        if burst_status is None:
            burst_status = BurstConfiguration2.BURST_FINISHED
        if error_message is not None:
            burst_status = BurstConfiguration2.BURST_ERROR

        try:
            ### If there are any DataType Groups in current Burst, update their counter.
            burst_dt_groups = dao.get_generic_entity(DataTypeGroup, burst_entity.id, "fk_parent_burst")
            for dt_group in burst_dt_groups:
                dt_group.count_results = dao.count_datatypes_in_group(dt_group.id)
                dt_group.disk_size, dt_group.subject = dao.get_summary_for_group(dt_group.id)
                dao.store_entity(dt_group)

            ### Update actual Burst entity fields
            burst_entity.datatypes_number = dao.count_datatypes_in_burst(burst_entity.id)

            burst_entity.status = burst_status
            burst_entity.error_message = error_message
            burst_entity.finish_time = datetime.now()
            dao.store_entity(burst_entity)
        except Exception:
            self.logger.exception("Could not correctly update Burst status and meta-data!")
            burst_entity.status = burst_status
            burst_entity.error_message = "Error when updating Burst Status"
            burst_entity.finish_time = datetime.now()
            dao.store_entity(burst_entity)

    def persist_operation_state(self, operation, operation_status, message=None):
        """
        Update Operation instance state. Store it in DB and on HDD/
        :param operation: Operation instance
        :param operation_status: new status
        :param message: message in case of error
        :return: operation instance changed
        """
        operation.mark_complete(operation_status, unicode(message))
        dao.store_entity(operation)
        operation = dao.get_operation_by_id(operation.id)
        self.file_helper.write_operation_metadata(operation)
        return operation
