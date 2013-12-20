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
.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
"""

from abc import abstractmethod
from tvb.core.adapters.abcadapter import ABCSynchronous
from tvb.core.entities.transient.structure_entities import DataTypeMetaData


class ABCUploader(ABCSynchronous):
    """
    Base class of the uploaders
    """
    def get_input_tree(self):
        """
        :return: the result of get_upload_input_tree concatenated with "subject" input field.
        """
        subject_node = [{'name': 'subject', 'type': 'str', 'required': True,
                         'label': 'Subject', 'default': DataTypeMetaData.DEFAULT_SUBJECT}]

        return subject_node + self.get_upload_input_tree()


    @abstractmethod
    def get_upload_input_tree(self):
        """
        Build the list of dictionaries describing the input required for this uploader.
        :return: The input tree specific for this uploader
        """


    def _prelaunch(self, operation, uid=None, available_disk_space=0, **kwargs):
        subject = kwargs.pop('subject')
        self.meta_data.update({DataTypeMetaData.KEY_SUBJECT: subject})
        return ABCSynchronous._prelaunch(self, operation, uid=None, **kwargs)


    def get_required_memory_size(self, **kwargs):
        """
        Return the required memory to run this algorithm.
        As it is an upload algorithm and we do not have information about data, we can not approximate this.
        """
        return -1


    def get_required_disk_size(self, **kwargs):
        """
        As it is an upload algorithm and we do not have information about data, we can not approximate this.
        """
        return 0