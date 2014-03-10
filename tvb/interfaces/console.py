
"""
Shortcut for activating the console profile on the console and conveniently
importing interacting with the full framework.

>>> import tvb.basic.console_profile as prof
>>> prof.attach_db_events()
>>> dao.get_foo()
...

"""

from tvb.basic.profile import TvbProfile as tvb_profile
tvb_profile.set_profile(["-profile", "CONSOLE_PROFILE"], try_reload=False)

from tvb.core.traits import db_events

from tvb.core.entities.model import *
from tvb.core.entities.storage import dao

from tvb.core.services.flow_service import FlowService
from tvb.core.services.operation_service import OperationService

from tvb.adapters.uploaders.abcuploader import ABCUploader

from tvb.basic.logger.builder import get_logger

db_events.attach_db_events()


