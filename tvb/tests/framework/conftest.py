# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
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
import numpy
import pytest
import os.path
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tvb.datatypes.connectivity import Connectivity
from tvb.datatypes.region_mapping import RegionMapping
from tvb.datatypes.sensors import Sensors
from tvb.datatypes.surfaces import Surface, CorticalSurface

from tvb.core.neotraits.db import Base


def pytest_addoption(parser):
    parser.addoption("--profile", action="store", default="TEST_SQLITE_PROFILE",
                     help="my option: TEST_POSTGRES_PROFILE or TEST_SQLITE_PROFILE")


@pytest.fixture(scope='session')
def profile(request):
    return request.config.getoption("--profile")


@pytest.fixture
def tmph5factory(tmpdir):
    def build(pth='tmp.h5'):
        path = os.path.join(str(tmpdir), pth)
        if os.path.exists(path):
            os.remove(path)
        return path

    return build


@pytest.fixture(scope='session')
def db_engine(tmpdir_factory, profile):
    if profile == 'TEST_SQLITE_PROFILE':
        tmpdir = tmpdir_factory.mktemp('tmp')
        path = os.path.join(str(tmpdir), 'tmp.sqlite')
        conn_string = r'sqlite:///' + path
    elif profile == 'TEST_POSTGRES_PROFILE':
        conn_string = 'postgresql+psycopg2://tvb:tvb23@localhost:5432/tvb'
    else:
        raise ValueError('bad test profile {}'.format(profile))

    return create_engine(conn_string)


@pytest.fixture
def session(db_engine):
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)
    Session = sessionmaker(bind=db_engine)
    s = Session()
    yield s
    s.close()
    Base.metadata.drop_all(db_engine)


@pytest.fixture()
def connectivityFactory():
    def build(nr_regions=4):
        return Connectivity(
            region_labels=numpy.array(["a"] * nr_regions),
            weights=numpy.zeros((nr_regions, nr_regions)),
            undirected=True,
            tract_lengths=numpy.zeros((nr_regions, nr_regions)),
            centres=numpy.zeros((nr_regions, nr_regions)),
            cortical=numpy.array([True] * nr_regions),
            hemispheres=numpy.array([True] * nr_regions),
            orientations=numpy.zeros((nr_regions, nr_regions)),
            areas=numpy.zeros((nr_regions * nr_regions,)),
            number_of_regions=nr_regions,
            number_of_connections=nr_regions * nr_regions,
            saved_selection=["a", "b", "C"]
        )

    return build


@pytest.fixture()
def surfaceFactory():
    def build(nr_vertices=10, valid_for_simulation=True, cortical=False):
        if cortical:
            return CorticalSurface(
                vertices=numpy.zeros((nr_vertices, 3)),
                triangles=numpy.zeros((3, 3), dtype=int),
                vertex_normals=numpy.zeros((nr_vertices, 3)),
                triangle_normals=numpy.zeros((3, 3)),
                number_of_vertices=nr_vertices,
                number_of_triangles=3,
                edge_mean_length=1.0,
                edge_min_length=0.0,
                edge_max_length=2.0,
                zero_based_triangles=False,
                split_triangles=numpy.arange(0),
                number_of_split_slices=1,
                split_slices=dict(),
                bi_hemispheric=False,
                # surface_type="surface",
                valid_for_simulations=True
            )

        return Surface(
            vertices=numpy.zeros((nr_vertices, 3)),
            triangles=numpy.zeros((3, 3), dtype=int),
            vertex_normals=numpy.zeros((nr_vertices, 3)),
            triangle_normals=numpy.zeros((3, 3)),
            number_of_vertices=nr_vertices,
            number_of_triangles=3,
            edge_mean_length=1.0,
            edge_min_length=0.0,
            edge_max_length=2.0,
            zero_based_triangles=False,
            split_triangles=numpy.arange(0),
            number_of_split_slices=1,
            split_slices=dict(),
            bi_hemispheric=False,
            surface_type="surface_cortical",
            valid_for_simulations=valid_for_simulation)

    return build


@pytest.fixture()
def regionMappingFactory(surfaceFactory, connectivityFactory):
    def build(surface=None, connectivity=None):
        if not surface:
            surface = surfaceFactory(5)
        if not connectivity:
            connectivity = connectivityFactory(2)
        return RegionMapping(
            array_data=numpy.arange(surface.number_of_vertices),
            connectivity=connectivity,
            surface=surface
        )

    return build


@pytest.fixture()
def sensorsFactory():
    def build(type="EEG", nr_sensors=3):
        return Sensors(
            sensors_type=type,
            labels=numpy.array(["s"] * nr_sensors),
            locations=numpy.ones((nr_sensors, 3)),
            number_of_sensors=nr_sensors,
            has_orientation=True,
            orientations=numpy.zeros((nr_sensors, 3)),
            usable=numpy.array([True] * nr_sensors)
        )

    return build
