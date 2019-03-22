import numpy
from tvb.datatypes.fcd import Fcd
from tvb.datatypes.time_series import TimeSeries
from tvb.core.entities.model.datatypes.connectivity import ConnectivityIndex
from tvb.core.entities.model.datatypes.fcd import FcdIndex
from tvb.core.entities.model.datatypes.region_mapping import RegionMappingIndex
from tvb.core.entities.model.datatypes.sensors import SensorsIndex
from tvb.core.entities.model.datatypes.surface import SurfaceIndex
from tvb.core.entities.model.datatypes.time_series import TimeSeriesIndex


def test_store_load_region_mapping(session, connectivityFactory, surfaceFactory, regionMappingFactory, sensorsFactory):
    connectivity = connectivityFactory(2)
    conn_idx = ConnectivityIndex()
    conn_idx.fill_from_has_traits(connectivity)
    session.add(conn_idx)

    surface = surfaceFactory(5)
    surf_idx = SurfaceIndex()
    surf_idx.fill_from_has_traits(surface)
    session.add(surf_idx)

    region_mapping = regionMappingFactory(surface, connectivity)
    rm_idx = RegionMappingIndex()
    rm_idx.fill_from_has_traits(region_mapping)
    rm_idx.connectivity = conn_idx
    rm_idx.surface = surf_idx
    session.add(rm_idx)

    sensors = sensorsFactory("SEEG", 3)
    sensors_seeg_idx = SensorsIndex()
    sensors_seeg_idx.fill_from_has_traits(sensors)
    session.add(sensors_seeg_idx)

    sensors_eeg = sensorsFactory("EEG", 3)
    sensors_eeg_idx = SensorsIndex()
    sensors_eeg_idx.fill_from_has_traits(sensors_eeg)
    session.add(sensors_eeg_idx)

    time_series = TimeSeries(data=numpy.arange(5))

    fcd = Fcd(
        array_data=numpy.arange(5),
        source=time_series,
    )

    ts_index = TimeSeriesIndex()
    ts_index.fill_from_has_traits(time_series)
    session.add(ts_index)

    fcd_index = FcdIndex()
    fcd_index.fill_from_has_traits(fcd)
    fcd_index.source = ts_index
    session.add(fcd_index)

    session.commit()

    res = session.query(ConnectivityIndex)
    assert res.count() == 1
    assert res[0].number_of_regions == 2
    assert res[0].number_of_connections == 4
    assert res[0].undirected is True
    assert res[0].weights.ndim == 2
    assert res[0].weights.length_1d == 2
    assert res[0].weights.length_2d == 2
    assert res[0].weights.length_3d is None

    res = session.query(SurfaceIndex)
    assert res.count() == 1

    res = session.query(RegionMappingIndex)
    assert res.count() == 1
