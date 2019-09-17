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
import h5py
import numpy
from tvb.datatypes.connectivity import Connectivity
from tvb.core.neotraits.h5 import H5File, DataSet, Reference
from tvb.basic.neotraits.api import NArray, Attr

_STR_DTYPE = h5py.string_dtype(encoding='utf-8')
ANNOTATION_DTYPE = numpy.dtype([('id', 'i'),
                                ('parent_id', 'i'),
                                ('parent_left', 'i'),
                                ('parent_right', 'i'),
                                ('relation', _STR_DTYPE),  # S16
                                ('label', _STR_DTYPE),  # S256
                                ('definition', _STR_DTYPE),  # S1024
                                ('synonym', _STR_DTYPE),  # S2048
                                ('uri', _STR_DTYPE),  # S256
                                ('synonym_tvb_left', 'i'),
                                ('synonym_tvb_right', 'i')
                                ])


class ConnectivityAnnotationsH5(H5File):
    """
    Ontology annotations for a Connectivity.
    """

    def __init__(self, path):
        super(ConnectivityAnnotationsH5, self).__init__(path)
        self.region_annotations = DataSet(NArray(dtype=ANNOTATION_DTYPE), self, name='region_annotations')
        self.connectivity = Reference(Attr(field_type=Connectivity), self, name="connectivity")

    def store_annotations(self, annotation_terms):
        annotations = [ann.to_tuple() for ann in annotation_terms]
        annotations = numpy.array(annotations, dtype=ANNOTATION_DTYPE)
        self.region_annotations.store(annotations)
