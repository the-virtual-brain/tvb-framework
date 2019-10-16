# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and 
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
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
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

from tvb.adapters.uploaders.abcuploader import ABCUploader, ABCUploaderForm
from tvb.adapters.uploaders.brco.parser import XMLParser
from tvb.core.adapters.exceptions import LaunchException
from tvb.core.entities.model.datatypes.connectivity import ConnectivityIndex
from tvb.core.entities.storage import transactional
from tvb.datatypes.annotations import ConnectivityAnnotations

from tvb.core.neotraits._forms import UploadField, DataTypeSelectField


class BRCOImporterForm(ABCUploaderForm):

    def __init__(self, prefix='', project_id=None):
        super(BRCOImporterForm, self).__init__(prefix, project_id)

        self.data_file = UploadField('.xml', self, name='data_file', required=True, label='Connectivity Annotations')
        self.connectivity = DataTypeSelectField(ConnectivityIndex, self, name='connectivity', required=True,
                                                label='Target Large Scale Connectivity',
                                                doc='The Connectivity for which these annotations were made')


class BRCOImporter(ABCUploader):
    """
    Import connectivity data stored in the networkx gpickle format
    """
    _ui_name = "BRCO Ontology Annotations"
    _ui_subsection = "brco_importer"
    _ui_description = "Import connectivity annotations from BRCO Ontology"

    form = None

    def get_input_tree(self): return None

    def get_upload_input_tree(self): return None

    def get_form(self):
        if self.form is None:
            return BRCOImporterForm
        return self.form

    def set_form(self, form):
        self.form = form

    #TODO: Following should be adjusted once annotations in tvb-library are migrated to neotraits
    def get_output(self):
        return [ConnectivityAnnotations]


    @transactional
    def launch(self, data_file, connectivity):
        try:
            result = ConnectivityAnnotations(connectivity=connectivity, storage_path=self.storage_path)
            parser = XMLParser(data_file, connectivity)
            annotations = parser.read_annotation_terms()
            result.set_annotations(annotations)
            return result
        except Exception as excep:
            self.log.exception("Could not process Connectivity Annotations")
            raise LaunchException(excep)
