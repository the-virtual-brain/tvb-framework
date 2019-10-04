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
import json
import numpy
import pytest
import os.path
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tvb.core.entities.model.model_operation import STATUS_FINISHED, Operation
from tvb.core.entities.model.model_project import User, Project
from tvb.core.entities.storage import dao
from tvb.core.entities.file.files_helper import FilesHelper
from tvb.core.entities.transient.structure_entities import DataTypeMetaData
from tvb.core.services.flow_service import FlowService
from tvb.core.services.project_service import ProjectService
from tvb.core.services.operation_service import OperationService
from tvb.datatypes.connectivity import Connectivity
from tvb.datatypes.region_mapping import RegionMapping
from tvb.datatypes.sensors import Sensors
from tvb.datatypes.surfaces import Surface, CorticalSurface
from tvb.simulator.simulator import Simulator
from tvb.tests.framework.core.base_testcase import TvbProfile


def pytest_addoption(parser):
    parser.addoption("--profile", action="store", default="TEST_SQLITE_PROFILE",
                     help="my option: TEST_POSTGRES_PROFILE or TEST_SQLITE_PROFILE")


@pytest.fixture(scope='session')
def profile(request):
    profile = request.config.getoption("--profile")
    TvbProfile.set_profile(profile)
    return profile


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


@pytest.fixture
def userFactory():
    def build(username='test_user', password='test_pass',
              mail='test_mail@tvb.org', validated=True, role='test'):
        """
        Create persisted User entity.
        :returns: User entity after persistence.
        """
        existing_user = dao.get_user_by_name(username)
        if existing_user is not None:
            return existing_user

        user = User(username, password, mail, validated, role)
        return dao.store_entity(user)

    return build


@pytest.fixture
def projectFactory():
    def build(admin, name="TestProject", description='description', users=None):
        """
        Create persisted Project entity, with no linked DataTypes.
        :returns: Project entity after persistence.
        """
        project = dao.get_generic_entity(Project, name, "name")
        if project:
            return project[0]

        if users is None:
            users = []
        data = dict(name=name, description=description, users=users)
        return ProjectService().store_project(admin, True, None, **data)

    return build


@pytest.fixture()
def operationFactory(userFactory, projectFactory):
    def build(algorithm=None, test_user=None, test_project=None,
              operation_status=STATUS_FINISHED, parameters="test params"):
        """
        Create persisted operation.
        :param algorithm: When not None, Simulator.
        :return: Operation entity after persistence.
        """
        if algorithm is None:
            algorithm = dao.get_algorithm_by_module('tvb.adapters.simulator.simulator_adapter', 'SimulatorAdapter')
        if test_user is None:
            test_user = userFactory()
        if test_project is None:
            test_project = projectFactory(test_user)

        meta = {DataTypeMetaData.KEY_SUBJECT: "John Doe",
                DataTypeMetaData.KEY_STATE: "RAW_DATA"}
        operation = Operation(test_user.id, test_project.id, algorithm.id, parameters, meta=json.dumps(meta),
                              status=operation_status)
        dao.store_entity(operation)
        # Make sure lazy attributes are correctly loaded.
        return dao.get_operation_by_id(operation.id)

    return build


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


@pytest.fixture()
def regionSimulationFactory(connectivityFactory):
    def build(connectivity=None, simulation_length=100):
        if not connectivity:
            connectivity = connectivityFactory(2)
        return Simulator(connectivity=connectivity,
                         surface=None,
                         simulation_length=simulation_length)
def ica_factory(operation_factory, time_series_factory):
    """
    :returns: persisted entity IndependentComponents
    """
    operation, _, storage_path = operation_factory
    partial_ts = TimeSeries(use_storage=False)
    partial_ts.data = numpy.random.random((10, 10, 10, 10))
    partial_ica = IndependentComponents(source=partial_ts,
                                        component_time_series=numpy.random.random((10, 10, 10, 10)),
                                        prewhitening_matrix=numpy.random.random((10, 10, 10, 10)),
                                        unmixing_matrix=numpy.random.random((10, 10, 10, 10)),
                                        n_components=10, use_storage=False)
    ica = IndependentComponents(source=time_series_factory, n_components=10, storage_path=storage_path)
    ica.write_data_slice(partial_ica)
    adapter_instance = StoreAdapter([ica])
    OperationService().initiate_prelaunch(operation, adapter_instance)
    return ica


@pytest.fixture(scope='module')
def datatype_group_factory(datatype_factory, define_attributes, datatype_with_storage_factory):

    def build(subject=define_attributes['USER_FULL_NAME'], state=define_attributes['DATATYPE_STATE'], ):

        """
        This method creates, stores and returns a DataTypeGroup entity.
        """
        group = OperationGroup(datatype_factory['project'].id, ranges=[json.dumps(define_attributes['RANGE_1']), json.dumps(define_attributes['RANGE_2'])])
        group = dao.store_entity(group)
        group_ms = OperationGroup(datatype_factory['project'].id, ranges=[json.dumps(define_attributes['RANGE_1']), json.dumps(define_attributes['RANGE_2'])])
        group_ms = dao.store_entity(group_ms)

        datatype_group = DataTypeGroup(group, subject=subject, state=state, operation_id=datatype_factory['operation'].id)
        # Set storage path, before setting data
        datatype_group.storage_path = datatype_factory['files_helper'].get_project_folder(datatype_factory['project'], str(datatype_factory['operation'].id))
        datatype_group = dao.store_entity(datatype_group)

        dt_group_ms = DataTypeGroup(group_ms, subject=subject, state=state, operation_id=datatype_factory['operation'].id)
        # Set storage path, before setting data
        dt_group_ms.storage_path = datatype_factory['files_helper'].get_project_folder(datatype_factory['project'], str(datatype_factory['operation'].id))
        dao.store_entity(dt_group_ms)

        # Now create some data types and add them to group
        for range_val1 in define_attributes['RANGE_1'][1]:
            for range_val2 in define_attributes['RANGE_2'][1]:
                operation = Operation(datatype_factory['user'].id, datatype_factory['project'].id, datatype_factory['algorithm'].id, 'test parameters',
                                    meta=json.dumps(datatype_factory['meta']), status=STATUS_FINISHED,
                                    range_values=json.dumps({define_attributes['RANGE_1'][0]: range_val1,
                                                            define_attributes['RANGE_2'][0]: range_val2}))
                operation.fk_operation_group = group.id
                operation = dao.store_entity(operation)
                datatype = datatype_with_storage_factory(operation_id=operation.id)
                datatype.number1 = range_val1
                datatype.number2 = range_val2
                datatype.fk_datatype_group = datatype_group.id
                datatype.set_operation_id(operation.id)
                dao.store_entity(datatype)

                op_ms = Operation(datatype_factory['user'].id, datatype_factory['project'].id, datatype_factory['algorithm'].id, 'test parameters',
                                meta=json.dumps(datatype_factory['meta']), status=STATUS_FINISHED,
                                  range_values=json.dumps({define_attributes['RANGE_1'][0]: range_val1,
                                                           define_attributes['RANGE_2'][0]: range_val2}))
                op_ms.fk_operation_group = group_ms.id
                op_ms = dao.store_entity(op_ms)
                datatype_measure_factory(datatype, op_ms,
                                             FilesHelper().get_project_folder(datatype_factory['project'], str(op_ms.id)))

        return datatype_group

    return build

@pytest.fixture(scope='session')
def define_attributes():

    return dict(USER_FULL_NAME="Datatype Factory User", DATATYPE_STATE="RAW_DATA",
                DATATYPE_DATA=["test", "for", "datatypes", "factory"], DATATYPE_MEASURE_METRIC={'v': 3},
                RANGE_1=["row1", [1, 2, 3]], RANGE_2=["row2", [0.1, 0.3, 0.5]],
                user=None, project=None, operation=None)

@pytest.fixture(scope='session', autouse=True)
def datatype_factory(define_attributes):

    def setup_method():

        micro_postfix = "_%d" % int(time.time() * 1000000)

        #Here create all structures needed later for data types creation
        files_helper = FilesHelper()

        #First create user
        user = dao.store_entity(User("datatype_factory_user" + micro_postfix, "test_pass",
                                 "test_mail@tvb.org" + micro_postfix, True, "user"))

        #Now create a project
        project_service = ProjectService()
        data = dict(name='DatatypesFactoryProject' + micro_postfix, description='test_desc', users=[])
        project = project_service.store_project(user, True, None, **data)

        #Create algorithm
        alg_category = AlgorithmCategory('one', True)
        dao.store_entity(alg_category)
        ad = Algorithm(IntrospectionRegistry.SIMULATOR_MODULE, IntrospectionRegistry.SIMULATOR_CLASS,
                       alg_category.id)
        algorithm = dao.get_algorithm_by_module(IntrospectionRegistry.SIMULATOR_MODULE,
                                            IntrospectionRegistry.SIMULATOR_CLASS)
        if algorithm is None:
            algorithm = dao.store_entity(ad)

        #Create an operation
        meta = {DataTypeMetaData.KEY_SUBJECT: define_attributes['USER_FULL_NAME'],
                 DataTypeMetaData.KEY_STATE: define_attributes['DATATYPE_STATE']}
        operation = dao.store_entity(Operation(user.id, project.id, algorithm.id, 'test parameters',
                                           meta=json.dumps(meta), status=STATUS_FINISHED))

        return dict(project=project, operation=operation, user=user, files_helper=files_helper, algorithm=algorithm, meta=meta)

    return setup_method()


@pytest.fixture(scope='module')
def datatype_store_factory(datatype_factory, define_attributes):

    def build(inst=None, subject=define_attributes['USER_FULL_NAME'],
                         state=define_attributes['DATATYPE_STATE'], operation_id=None):

        inst = inst or ValueWrapperIndex()
        inst.subject = subject or define_attributes['USER_FULL_NAME']
        inst.state = state or define_attributes['DATATYPE_STATE']
        inst.fk_from_operation = operation_id or datatype_factory['operation'].id
        inst.type = inst.__class__.__name__
        inst.module = inst.__class__.__module__
        dao.store_entity(inst)
        return inst

    return build

@pytest.fixture(scope='module')
def datatype_fill_factory(datatype_factory):

    def build(datatype, subject, state, operation_id=None):
        """
        This method sets some common attributes on dataType
        """
        operation_id = operation_id or datatype_factory['operation'].id
        datatype.subject = subject
        datatype.state = state
        # Set_operation_id also sets storage_path attribute
        datatype.id = operation_id

    return build

@pytest.fixture(scope='module')
def simple_datatype_factory(datatype_store_factory, define_attributes, datatype_fill_factory):

    def build(subject=define_attributes['USER_FULL_NAME'], state=define_attributes['DATATYPE_STATE']):
        """
        This method creates a simple data type
        """
        datatype_inst = Datatype1()
        datatype_fill_factory(datatype_inst, subject, state)

        # Store data type
        return datatype_store_factory(datatype_inst)

    return build

@pytest.fixture(scope='module')
def datatype_with_storage_factory(datatype_store_factory, define_attributes, datatype_fill_factory):

    def build(subject=define_attributes['USER_FULL_NAME'], state=define_attributes['DATATYPE_STATE'],
              data=define_attributes['DATATYPE_DATA'], operation_id=None):
        """
                This method creates and stores a data type which imply storage on the file system.
                """
        datatype_inst = Datatype2()
        datatype_fill_factory(datatype_inst, subject, state, operation_id)

        datatype_inst.string_data = data
        return datatype_store_factory(datatype_inst, operation_id)

    return build

@pytest.fixture(scope='module')
def operation_factory(datatype_factory):

    def build():
        """
        Create a operation entity. Return the operation, algo_id and the storage path.
        """
        meta = {DataTypeMetaData.KEY_SUBJECT: "John Doe", DataTypeMetaData.KEY_STATE: "RAW_DATA"}
        algorithm = FlowService().get_algorithm_by_module_and_class(IntrospectionRegistry.SIMULATOR_MODULE,
                                                                    IntrospectionRegistry.SIMULATOR_CLASS)
        operation = Operation(datatype_factory['user'].id, datatype_factory['project'].id, algorithm.id, json.dumps(''), meta=json.dumps(meta),
                              status=STATUS_STARTED)
        operation = dao.store_entity(operation)
        storage_path = FilesHelper().get_project_folder(datatype_factory['project'], str(operation.id))
        return operation, algorithm.id, storage_path

    return build

@pytest.fixture(scope='module')
def connectivity_factory(operation_factory):

    def build(nodes=74):
        """
        Create a connectivity that will be used in "non-dummy" burst launches (with the actual simulator).
        """
        operation, algo_id, storage_path = operation_factory
        connectivity = Connectivity()
        connectivity.weights = numpy.ones((nodes, nodes))
        connectivity.centres = numpy.ones((nodes, 3))
        adapter_instance = StoreAdapter([connectivity])
        operation_service = OperationService()
        operation_service.initiate_prelaunch(operation, adapter_instance)
        return algo_id, connectivity

    return build

@pytest.fixture(scope='module')
def time_series_factory(operation_factory, connectivity_factory):

    def build(ts_type=None, sensors=None):
        """
        Create a stored TimeSeries entity.
        """
        operation, _, storage_path = operation_factory

        if ts_type == "EEG":
            time_series = TimeSeriesEEG(storage_path=storage_path, sensors=sensors)
        else:
            rm = dao.get_generic_entity(RegionMapping, connectivity_factory.gid, '_connectivity')
            if len(rm) < 1:
                rm = None
            else:
                rm = rm[0]
            time_series = TimeSeriesRegion(storage_path=storage_path, connectivity=connectivity_factory, region_mapping=rm)

        data = numpy.random.random((10, 10, 10, 10))
        time_series.write_data_slice(data)
        time_series.write_time_slice(numpy.arange(10))
        adapter_instance = StoreAdapter([time_series])
        OperationService().initiate_prelaunch(operation, adapter_instance)
        time_series = dao.get_datatype_by_gid(time_series.gid)
        return time_series

    return build

@pytest.fixture
def stimulus_factory(connectivity_factory):
    """
    :param connectivity: Connectivity to create stimuli for its regions
    :return: persisted region Stimuli instance
    """

    operation, _, storage_path = operation_factory()
    stimuli_region = StimuliRegion(storage_path=storage_path)
    stimuli_region.connectivity = connectivity_factory
    stimuli_region.weight = numpy.random.random((connectivity_factory.number_of_region, 1)).tolist()
    stimuli_region.temporal = PulseTrain()

    adapter_instance = StoreAdapter([stimuli_region])
    OperationService().initiate_prelaunch(operation, adapter_instance)
    return stimuli_region

@pytest.fixture
def covariance_factory():
    """
    :returns: a stored DataType Covariance.
    """
    operation, _, storage_path = operation_factory()
    covariance = Covariance(storage_path=storage_path, source=time_series_factory())
    covariance.write_data_slice(numpy.random.random((10, 10, 10)))
    adapter_instance = StoreAdapter([covariance])
    OperationService().initiate_prelaunch(operation, adapter_instance)
    return covariance

@pytest.fixture
def cross_coherence_factory():
    """
    :returns: a stored entity of type CoherenceSpectrum
    """
    operation, _, storage_path = operation_factory()
    partial_coh = CoherenceSpectrum(array_data=numpy.random.random((10, 10, 10, 10)), use_storage=False)
    coherence = CoherenceSpectrum(source=time_series_factory, storage_path=storage_path, frequency=0.1, nfft=256)
    coherence.write_data_slice(partial_coh)
    coherence.close_file()
    adapter_instance = StoreAdapter([coherence])
    OperationService().initiate_prelaunch(operation, adapter_instance)
    return coherence

@pytest.fixture
def cross_correlation_factory():
    """
    :returns: `CrossCorrelation` stored entity.
    """
    operation, _, storage_path = operation_factory()
    partial_corr = CrossCorrelation(array_data=numpy.random.random((10, 10, 10, 10, 10)), use_storage=False)
    crossc = CrossCorrelation(source=time_series_factory, storage_path=storage_path, time=range(10))
    crossc.write_data_slice(partial_corr)
    crossc.close_file()
    adapter_instance = StoreAdapter([crossc])
    OperationService().initiate_prelaunch(operation, adapter_instance)
    return crossc

@pytest.fixture
def surface_factory(operation_factory):
    """
    Create a dummy surface entity.
    :returns: (Algorithm Identifier, stored Surface entity)
    """
    operation, algo_id, storage_path = operation_factory
    surface = CorticalSurface(storage_path=storage_path)
    surface.vertices = numpy.array([[-10, 0, 0],
                                    [0, 0, -10],
                                    [10, 0, 0],
                                    [0, 10, 0]], dtype=float)
    surface.triangles = numpy.array([[0, 1, 2],
                                     [0, 1, 3],
                                     [1, 2, 3],
                                     [0, 2, 3]], dtype=int)
    surface.number_of_triangles = 4
    surface.number_of_vertices = 4
    surface.triangle_normals = numpy.ones((4, 3))
    surface.vertex_normals = numpy.ones((4, 3))
    surface.zero_based_triangles = True
    surface.validate()
    adapter_instance = StoreAdapter([surface])
    OperationService().initiate_prelaunch(operation, adapter_instance)
    return algo_id, surface

@pytest.fixture()
def connectivity_measure_factory():
    """
    :returns: persisted entity ConnectivityMeasure
    """
    operation, _, storage_path = operation_factory()
    conn_measure = ConnectivityMeasure(storage_path=storage_path)
    conn_measure.connectivity = connectivity_factory()
    adapter_instance = StoreAdapter([conn_measure])
    OperationService().initiate_prelaunch(operation, adapter_instance)
    return conn_measure

@pytest.fixture()
def datatype_measure_factory(operation_factory):

    def build(analyzed_entity, operation=None):

        """
        :return: persisted DatatypeMeasure
        """
        if operation is None:
            operation, _, storage_path = operation_factory
        measure = DatatypeMeasureIndex()
        measure.metrics = define_attributes.DATATYPE_MEASURE_METRIC
        measure.source = analyzed_entity
        adapter_instance = StoreAdapter([measure])
        OperationService().initiate_prelaunch(operation, adapter_instance)
        return measure

    return build

@pytest.fixture()
def ica_factory(operation_factory, time_series_factory):
    """
    :returns: persisted entity IndependentComponents
    """
    operation, _, storage_path = operation_factory
    partial_ts = TimeSeries(use_storage=False)
    partial_ts.data = numpy.random.random((10, 10, 10, 10))
    partial_ica = IndependentComponents(source=partial_ts,
                                        component_time_series=numpy.random.random((10, 10, 10, 10)),
                                        prewhitening_matrix=numpy.random.random((10, 10, 10, 10)),
                                        unmixing_matrix=numpy.random.random((10, 10, 10, 10)),
                                        n_components=10, use_storage=False)
    ica = IndependentComponents(source=time_series_factory, n_components=10, storage_path=storage_path)
    ica.write_data_slice(partial_ica)
    adapter_instance = StoreAdapter([ica])
    OperationService().initiate_prelaunch(operation, adapter_instance)
    return ica


@pytest.fixture(scope='module')
def datatype_group_factory(datatype_factory, define_attributes, datatype_with_storage_factory):

    def build(subject=define_attributes['USER_FULL_NAME'], state=define_attributes['DATATYPE_STATE'], ):

        """
        This method creates, stores and returns a DataTypeGroup entity.
        """
        group = OperationGroup(datatype_factory['project'].id, ranges=[json.dumps(define_attributes['RANGE_1']), json.dumps(define_attributes['RANGE_2'])])
        group = dao.store_entity(group)
        group_ms = OperationGroup(datatype_factory['project'].id, ranges=[json.dumps(define_attributes['RANGE_1']), json.dumps(define_attributes['RANGE_2'])])
        group_ms = dao.store_entity(group_ms)

        datatype_group = DataTypeGroup(group, subject=subject, state=state, operation_id=datatype_factory['operation'].id)
        # Set storage path, before setting data
        datatype_group.storage_path = datatype_factory['files_helper'].get_project_folder(datatype_factory['project'], str(datatype_factory['operation'].id))
        datatype_group = dao.store_entity(datatype_group)

        dt_group_ms = DataTypeGroup(group_ms, subject=subject, state=state, operation_id=datatype_factory['operation'].id)
        # Set storage path, before setting data
        dt_group_ms.storage_path = datatype_factory['files_helper'].get_project_folder(datatype_factory['project'], str(datatype_factory['operation'].id))
        dao.store_entity(dt_group_ms)

        # Now create some data types and add them to group
        for range_val1 in define_attributes['RANGE_1'][1]:
            for range_val2 in define_attributes['RANGE_2'][1]:
                operation = Operation(datatype_factory['user'].id, datatype_factory['project'].id, datatype_factory['algorithm'].id, 'test parameters',
                                    meta=json.dumps(datatype_factory['meta']), status=STATUS_FINISHED,
                                    range_values=json.dumps({define_attributes['RANGE_1'][0]: range_val1,
                                                            define_attributes['RANGE_2'][0]: range_val2}))
                operation.fk_operation_group = group.id
                operation = dao.store_entity(operation)
                datatype = datatype_with_storage_factory(operation_id=operation.id)
                datatype.number1 = range_val1
                datatype.number2 = range_val2
                datatype.fk_datatype_group = datatype_group.id
                datatype.set_operation_id(operation.id)
                dao.store_entity(datatype)

                op_ms = Operation(datatype_factory['user'].id, datatype_factory['project'].id, datatype_factory['algorithm'].id, 'test parameters',
                                meta=json.dumps(datatype_factory['meta']), status=STATUS_FINISHED,
                                  range_values=json.dumps({define_attributes['RANGE_1'][0]: range_val1,
                                                           define_attributes['RANGE_2'][0]: range_val2}))
                op_ms.fk_operation_group = group_ms.id
                op_ms = dao.store_entity(op_ms)
                datatype_measure_factory(datatype, op_ms,
                                             FilesHelper().get_project_folder(datatype_factory['project'], str(op_ms.id)))

        return datatype_group

    return build
