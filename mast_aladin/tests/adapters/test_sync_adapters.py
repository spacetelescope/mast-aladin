from astropy.coordinates import SkyCoord
from mast_aladin.adapters import AladinSyncAdapter, ImvizSyncAdapter
from mast_aladin.app import MastAladin
from mast_aladin.tests.test_utils import BaseImviz
from mast_aladin.aida import AIDA_aspect

from pytest import approx
import warnings


class TestSyncAdapters(BaseImviz):
    def test_aladin_sync_from_imviz(self):
        # arrange
        target = SkyCoord(9.4213055, -33.71625419, unit="deg")
        MastAladin(target=target, height=500)
        mast_aladin_sync_adapter = AladinSyncAdapter()
        mast_aladin_sync_adapter.viewer._fov_xy = {'x': 60, 'y': 12.583892617449665}

        imviz_sync_adapter = ImvizSyncAdapter()
        imviz_sync_adapter.app.link_data(align_by='wcs')

        # assert starting coordinate is approximately on Cartwheel Galaxy
        center = mast_aladin_sync_adapter.aid.get_viewport()[AIDA_aspect.CENTER]
        assert center.ra.deg == approx(9.4213055, rel=1e-8)
        assert center.dec.deg == approx(-33.71625419, rel=1e-8)

        # act - sync the mast aladin viewer to the imviz view
        with warnings.catch_warnings(record=True) as w:
            mast_aladin_sync_adapter.sync_to(imviz_sync_adapter)
            assert len(w) == 1

        # assert that the view has changed as expected
        center = mast_aladin_sync_adapter.viewer.target
        assert center.ra.deg == approx(9.425937637864708, rel=1e-8)
        assert center.dec.deg == approx(-33.71515927986813, rel=1e-8)

    def test_aladin_sync_to_imviz(self):
        # arrange
        target = SkyCoord(9.4213055, -33.71625419, unit="deg")
        MastAladin(target=target, height=500)
        mast_aladin_sync_adapter = AladinSyncAdapter()
        mast_aladin_sync_adapter.viewer._fov_xy = {'x': 60, 'y': 12.583892617449665}

        imviz_sync_adapter = ImvizSyncAdapter()
        imviz_sync_adapter.app.link_data(align_by='wcs')

        # assert starting coordinate is approximately on Cartwheel Galaxy
        center = imviz_sync_adapter.aid.get_viewport(sky_or_pixel="sky")[AIDA_aspect.CENTER]
        assert center.ra.deg == approx(9.425937637864708, rel=1e-8)
        assert center.dec.deg == approx(-33.71515927986813, rel=1e-8)

        # act - sync the imviz viewer to the mast aladin viewer
        imviz_sync_adapter.sync_to(mast_aladin_sync_adapter)

        # assert that the view has changed as expected
        center = imviz_sync_adapter.aid.get_viewport(sky_or_pixel="sky")[AIDA_aspect.CENTER]
        assert center.ra.deg == approx(9.4213054999, rel=1e-8)
        assert center.dec.deg == approx(-33.71625419, rel=1e-8)
