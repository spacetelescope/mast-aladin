from astropy.table import Table
from astropy.coordinates import SkyCoord, Angle
import astropy.units as u
import pytest
from unittest.mock import Mock
import warnings
import re

from mast_aladin import MastAladin
from mast_aladin.overlay.mast_overlay import MastOverlay, MastOverlayType
from ipyaladin.elements.error_shape import EllipseError, CircleError
from regions import CircleSkyRegion
from ipyaladin import Marker


mast_aladin = MastAladin()
mast_aladin._is_loaded = True


def test_overlays_dict_add_markers(
    monkeypatch,
):
    """Test overlays_dict overlay info from adding markers."""
    test_name = "test"
    mock_send = Mock()
    monkeypatch.setattr(MastAladin, "send", mock_send)

    markers = []
    for i in range(1, 11):
        name = f"M{i}"
        markers.append(
            Marker(
                position=name,
                title=name,
                description=(
                    '<a href="https://simbad.cds.unistra.fr/simbad/'
                    f'sim-basic?Ident={name}&submit=SIMBAD+search"> '
                    "Read more on SIMBAD</a>"
                ),
            )
        )
    options = {"name": test_name, "color": "pink", "shape": "cross", "source_size": 15}

    mast_aladin.add_markers(markers, name=test_name, color="pink", shape="cross", source_size=15)

    assert test_name in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict[test_name]["type"] == "marker"
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_marker"
    assert sent_message["options"] == options

    # test handling for a catalog with existing name
    with warnings.catch_warnings(record=True) as w:
        mast_aladin.add_markers(
            markers,
            name=test_name,
            color="pink",
            shape="cross",
            source_size=15
        )
        assert len(w) == 1
        assert test_name + "_1" in str(w[-1].message)

    assert test_name + "_1" in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict[test_name + "_1"]["type"] == "marker"
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_marker"
    options["name"] = test_name + "_1"
    assert sent_message["options"] == options

    # test handling for catalog with no given name
    options["name"] = "catalog_python"
    mast_aladin.add_markers(markers, color="pink", shape="cross", source_size=15)

    assert "catalog_python" in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict["catalog_python"]["type"] == "marker"
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_marker"
    assert sent_message["options"] == options

    # test removing these overlays, resetting for next functionality check
    mast_aladin.remove_overlay([test_name, test_name + "_1", "catalog_python"])
    assert not mast_aladin._overlays_dict.keys()


def test_overlays_dict_add_catalog_from_URL(
    monkeypatch,
):
    """Test overlays_dict overlay info from adding catalog using its URL."""
    test_name = "test"
    mock_send = Mock()
    monkeypatch.setattr(MastAladin, "send", mock_send)

    url = (
        "https://vizier.unistra.fr/viz-bin/votable?-source=HIP2&-c=LMC&-out.add=_RAJ,_"
        "DEJ&-oc.form=dm&-out.meta=DhuL&-out.max=9999&-c.rm=180"
    )
    options = {"source_size": 12, "color": "#f08080", "on_click": "showTable", "name": test_name}
    mast_aladin.add_catalog_from_URL(url, options)

    assert test_name in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict[test_name]["type"] == "catalog"
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_catalog_from_URL"
    assert sent_message["votable_URL"] == url
    assert sent_message["options"] == options

    # test handling for a catalog with existing name
    with warnings.catch_warnings(record=True) as w:
        mast_aladin.add_catalog_from_URL(url, options)
        assert len(w) == 1
        assert test_name + "_1" in str(w[-1].message)

    assert test_name + "_1" in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict[test_name + "_1"]["type"] == "catalog"
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_catalog_from_URL"
    assert sent_message["votable_URL"] == url
    options["name"] = test_name + "_1"
    assert sent_message["options"] == options

    # test handling for catalog with no given name
    options.pop("name")
    mast_aladin.add_catalog_from_URL(url, options)

    assert "catalog_python" in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict["catalog_python"]["type"] == "catalog"
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_catalog_from_URL"
    assert sent_message["votable_URL"] == url
    options["name"] = "catalog_python"
    assert sent_message["options"] == options

    # test removing these overlays, resetting for next functionality check
    mast_aladin.remove_overlay([test_name, test_name + "_1", "catalog_python"])
    assert not mast_aladin._overlays_dict.keys()


def test_overlays_dict_add_table(monkeypatch):
    """Test overlays_dict overlay info from a table."""
    test_name = "test"
    table = Table({"a": [1, 2, 3]})
    table["a"].unit = "deg"
    mock_send = Mock()
    monkeypatch.setattr(MastAladin, "send", mock_send)

    # normal table call
    mast_aladin.add_table(table, name=test_name)
    sent_message = mock_send.call_args[0][0]
    assert sent_message["event_name"] == "add_table"

    assert test_name in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict[test_name]["type"] == "table"
    assert all(mast_aladin._overlays_dict[test_name]["table"] == table)

    # circle error
    # test handling for an overlay with existing name
    with warnings.catch_warnings(record=True) as w:
        mast_aladin.add_table(
            table,
            shape=CircleError(radius="a", default_shape="cross"),
            color="pink",
            name=test_name,
        )
        assert len(w) == 1
        assert test_name + "_1" in str(w[-1].message)

    sent_message = mock_send.call_args[0][0]
    assert sent_message["options"]["circle_error"] == {
        "radius": "a",
        "conversion_radius": 1,
    }
    assert sent_message["options"]["shape"] == "cross"

    assert test_name + "_1" in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict[test_name + "_1"]["type"] == "table"
    assert all(mast_aladin._overlays_dict[test_name + "_1"]["table"] == table)
    assert mast_aladin._overlays_dict[test_name + "_1"]["options"]["color"] == "pink"
    assert "circle_error" in mast_aladin._overlays_dict[test_name + "_1"]["options"]

    # ellipse error
    mast_aladin.add_table(table, shape=EllipseError(maj_axis="a", min_axis="a", angle="a"))
    sent_message = mock_send.call_args[0][0]
    ellipse_options = {
        "maj_axis": "a",
        "min_axis": "a",
        "angle": "a",
        "conversion_angle": 1,
        "conversion_min_axis": 1,
        "conversion_maj_axis": 1,
    }
    assert sent_message["options"]["ellipse_error"] == ellipse_options

    assert "catalog_python" in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict["catalog_python"]["type"] == "table"
    assert all(mast_aladin._overlays_dict["catalog_python"]["table"] == table)

    # test removing these overlays, resetting for next functionality check
    mast_aladin.remove_overlay([test_name, test_name + "_1", "catalog_python"])
    assert not mast_aladin._overlays_dict.keys()


def test_overlays_dict_add_graphic_overlay_from_region(
    monkeypatch,
):
    """Test overlays_dict overlay info from adding region overlay."""
    test_name = "test"
    mock_send = Mock()
    monkeypatch.setattr(MastAladin, "send", mock_send)

    center = SkyCoord.from_name("M31")
    radius = Angle(0.5, "deg")
    circle = CircleSkyRegion(
        center=center, radius=Angle(0.5, "deg"), visual={"edgecolor": "yellow"}
    )
    mast_aladin.add_graphic_overlay_from_region([circle], name=test_name)

    assert test_name in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict[test_name]["type"] == "overlay_region"
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert regions_info == mast_aladin._overlays_dict[test_name]["regions_infos"]
    assert regions_info[0]["infos"]["ra"] == center.ra.to_value(u.deg)
    assert regions_info[0]["infos"]["dec"] == center.dec.to_value(u.deg)
    assert regions_info[0]["infos"]["radius"] == radius.to_value(u.deg)

    # test handling for an overlay with existing name
    with warnings.catch_warnings(record=True) as w:
        mast_aladin.add_graphic_overlay_from_region([circle], name=test_name)
        assert len(w) == 1
        assert test_name + "_1" in str(w[-1].message)

    assert test_name + "_1" in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict[test_name + "_1"]["type"] == "overlay_region"
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert regions_info == mast_aladin._overlays_dict[test_name + "_1"]["regions_infos"]
    assert regions_info[0]["infos"]["ra"] == center.ra.to_value(u.deg)
    assert regions_info[0]["infos"]["dec"] == center.dec.to_value(u.deg)
    assert regions_info[0]["infos"]["radius"] == radius.to_value(u.deg)

    # test handling for overlay with no given name
    mast_aladin.add_graphic_overlay_from_region([circle])

    assert "overlay_python" in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict["overlay_python"]["type"] == "overlay_region"
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert regions_info == mast_aladin._overlays_dict["overlay_python"]["regions_infos"]
    assert regions_info[0]["infos"]["ra"] == center.ra.to_value(u.deg)
    assert regions_info[0]["infos"]["dec"] == center.dec.to_value(u.deg)
    assert regions_info[0]["infos"]["radius"] == radius.to_value(u.deg)

    # test removing these overlays, resetting for next functionality check
    mast_aladin.remove_overlay([test_name, test_name + "_1", "overlay_python"])
    assert not mast_aladin._overlays_dict.keys()


test_stcs_iterables = [
    "CIRCLE ICRS 258.93205686 43.13632863 0.625",
]


@pytest.mark.parametrize("stcs_strings", test_stcs_iterables)
def test_overlays_dict_add_graphic_overlay_from_stcs_(
    monkeypatch,
    stcs_strings,
):
    """Test overlays_dict overlay info from adding iterable STC-S string(s).

    Parameters
    ----------
    stcs_strings : Union[Iterable[str], str]
        The stcs strings to create region overlay info from.

    """
    test_name = "test"
    mock_send = Mock()
    monkeypatch.setattr(MastAladin, "send", mock_send)
    mast_aladin.add_graphic_overlay_from_stcs(stcs_strings, name=test_name)

    assert test_name in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict[test_name]["type"] == "overlay_stcs"
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert regions_info == mast_aladin._overlays_dict[test_name]["regions_infos"]
    assert regions_info[0]["infos"]["stcs"] in stcs_strings

    # test handling for an overlay with existing name
    with warnings.catch_warnings(record=True) as w:
        mast_aladin.add_graphic_overlay_from_stcs(stcs_strings, name=test_name)
        assert len(w) == 1
        assert test_name + "_1" in str(w[-1].message)

    assert test_name + "_1" in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict[test_name + "_1"]["type"] == "overlay_stcs"
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert regions_info == mast_aladin._overlays_dict[test_name + "_1"]["regions_infos"]
    assert regions_info[0]["infos"]["stcs"] in stcs_strings

    # test handling for overlay with no given name
    mast_aladin.add_graphic_overlay_from_stcs(stcs_strings)

    assert "overlay_python" in mast_aladin._overlays_dict
    assert mast_aladin._overlays_dict["overlay_python"]["type"] == "overlay_stcs"
    regions_info = mock_send.call_args[0][0]["regions_infos"]
    assert regions_info == mast_aladin._overlays_dict["overlay_python"]["regions_infos"]
    assert regions_info[0]["infos"]["stcs"] in stcs_strings

    # test removing these overlays, resetting for next functionality check
    mast_aladin.remove_overlay([test_name, test_name + "_1", "overlay_python"])
    assert not mast_aladin._overlays_dict.keys()


def test_invalid_overlay_type(
    monkeypatch,
):
    """Test proper error sent for adding invalid overlay type."""

    mock_send = Mock()
    monkeypatch.setattr(MastAladin, "send", mock_send)

    test_invalid_overlay = {
        "type": "not_valid",
        "options": {"name": "test_invalid"}
    }

    # try creating invalid layer to confirm error is raised
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Invalid overlay type 'not_valid'. "
            f"Must be one of {[t.value for t in MastOverlayType]}."
        )
    ):
        MastOverlay(test_invalid_overlay, mast_aladin)


test_marker_overlay = MastOverlay(
    {
        "type": "marker",
        "options": {"name": "test_markers"}
    },
    mast_aladin,
)


test_catalog_overlay = MastOverlay(
    {
        "type": "catalog",
        "options": {"name": "test_catalog"}
    },
    mast_aladin,
)


test_overlays = [
    "overlay",
    test_marker_overlay,
    ["overlay", "overlay_1", "2MASS"],
    "catalog",
    ["overlay_1", "2MASS", test_catalog_overlay],
]


@pytest.mark.parametrize("overlays", test_overlays)
def test_remove_overlay(
    monkeypatch,
    overlays,
):
    """Test proper messages sent for removing overlays.

    Parameters
    ----------
    overlays : Union[Iterable[str, MastOverlay], str, MastOverlay]
        The name strings of overlays.
    """
    mock_send = Mock()
    monkeypatch.setattr(MastAladin, "send", mock_send)

    # generate expected overlays_dict to remove names from
    if isinstance(overlays, MastOverlay):
        overlay_names = [overlays.name]
    elif isinstance(overlays, str):
        overlay_names = [overlays]
    elif isinstance(overlays, (list, tuple)):
        overlay_names = [
            o.name if isinstance(o, MastOverlay) else o for o in overlays
        ]

    mast_aladin._overlays_dict = {name: {} for name in overlay_names}

    mast_aladin.remove_overlay(overlay_names)

    event_name = mock_send.call_args[0][0]["event_name"]
    assert isinstance(event_name, str)
    assert event_name == "remove_overlay"

    name_info = mock_send.call_args[0][0]["overlay_names"]
    assert isinstance(name_info, list)
    assert name_info[0] in overlay_names

    if isinstance(overlay_names, list):
        assert name_info == overlay_names

    # confirm each overlay was removed from the dict as expected
    assert not mast_aladin._overlays_dict.keys()

    # try removing non-existent layer to confirm error is raised
    with pytest.raises(
        ValueError,
        match="Cannot remove overlayer `does_not_exist` "
        "since this layer does not exist.",
    ):
        mast_aladin.remove_overlay("does_not_exist")
