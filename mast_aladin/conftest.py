import os
import pytest
from astropy.table import Table
from mast_aladin import MastAladin
import jdaviz


@pytest.fixture
def MastAladin_app():
    return MastAladin()


@pytest.fixture
def imviz_helper():
    return jdaviz.gca()


@pytest.fixture
def mast_observation_table():
    """
    To reproduce the table file, run:

        from astroquery.mast.missions import MastMissions

        mast = MastMissions(mission='jwst')
        result = mast.query_object("M4", limit=5)
        result.write("mm_jwst_M4.ecsv")
    """
    path = os.path.join(
        os.path.dirname(__file__), "tests", "data", "mm_jwst_M4.ecsv"
    )
    return Table.read(path)
