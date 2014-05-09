<<<<<<< HEAD
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
.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

Shortcut for activating the console profile on the console and conveniently
importing interacting with the full framework.

>>> import tvb.basic.console_profile as prof
>>> prof.attach_db_events()
>>> dao.get_foo()
...

"""

=======
"""
tvb.console
-----------

Provides convenient access to framework from the console. 

"""

## Select the profile with storage enabled, but without web interface:
>>>>>>> bcbe888501607d2593180265b7432448f21b31ea
from tvb.basic.profile import TvbProfile as tvb_profile
tvb_profile.set_profile(["-profile", "CONSOLE_PROFILE"], try_reload=False)

from tvb.core.traits import db_events
<<<<<<< HEAD

from tvb.core.entities.model import *
from tvb.core.entities.storage import dao

from tvb.core.services.flow_service import FlowService
from tvb.core.services.operation_service import OperationService

from tvb.adapters.uploaders.abcuploader import ABCUploader

from tvb.basic.logger.builder import get_logger

db_events.attach_db_events()


=======
from tvb.core.entities.model import AlgorithmGroup, Algorithm
from tvb.core.entities.storage import dao
from tvb.core.services.flow_service import FlowService
from tvb.core.services.operation_service import OperationService

# Hook DB events (like prepare json attributes on traited DataTypes):
db_events.attach_db_events()


# Take from Lia's example. How to provide more functionality in
# a convenient way for the console user?
"""
    flow_service = FlowService()
    operation_service = OperationService()

    ## This ID of a project needs to exists in Db, and it can be taken from the WebInterface:
    project = dao.get_project_by_id(1)

    ## This is our new added Importer:
    adapter_instance = FooDataImporter()
    ## We need to store a reference towards the new algorithms also in DB:
    # First select the category of uploaders:
    upload_category = dao.get_uploader_categories()[0]
    # check if the algorithm has been added in DB already
    my_group = dao.find_group(FooDataImporter.__module__, FooDataImporter.__name__)
    if my_group is None:
        # not stored in DB previously, we will store it now:
        my_group = AlgorithmGroup(FooDataImporter.__module__, FooDataImporter.__name__, upload_category.id)
        my_group = dao.store_entity(my_group)
        dao.store_entity(Algorithm(my_group.id, "", "FooName"))

    adapter_instance.algorithm_group = my_group

    ## Prepare the input algorithms as if they were coming from web UI submit:
    #launch_args = {"array_data": "[1, 2, 3, 4, 5]"}
    launch_args = {"array_data" : "demo_array.txt"}

    ## launch an operation and have the results sotored both in DB and on disk
    launched_operations = flow_service.fire_operation(adapter_instance,
                                                      project.administrator,
                                                      project.id,
                                                      **launch_args)
"""
>>>>>>> bcbe888501607d2593180265b7432448f21b31ea
