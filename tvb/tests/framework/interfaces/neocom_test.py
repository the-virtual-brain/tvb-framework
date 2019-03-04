import os
import numpy
from tvb.interfaces.neocom.h5 import load, store, load_from_dir, store_to_dir
from tvb.tests.framework.core.entities.file.datatypes import testdatatypes


def test_store_load(tmpdir):
    path = os.path.join(str(tmpdir), 'interface.conn.h5')
    store(testdatatypes.connectivity, path)
    con2 = load(path)
    numpy.testing.assert_equal(testdatatypes.connectivity.weights, con2.weights)


def test_store_load_rec(tmpdir):
    store_to_dir(str(tmpdir), testdatatypes.region_mapping, recursive=True)

    rmap = load_from_dir(str(tmpdir), testdatatypes.region_mapping.gid, recursive=True)
    numpy.testing.assert_equal(testdatatypes.connectivity.weights, rmap.connectivity.weights)


