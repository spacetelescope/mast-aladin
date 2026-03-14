from enum import Enum


class MastOverlayType(Enum):
    MARKER = "marker"
    CATALOG = "catalog"
    TABLE = "table"
    OVERLAY_REGION = "overlay_region"
    OVERLAY_STCS = "overlay_stcs"


class MastOverlay(dict):
    """Dictionary describing an overlay within `mast_aladin.MastAladin`."""
    def __init__(self, overlay_info, mast_aladin):
        self.app = mast_aladin
        overlay_type = overlay_info.get("type")
        if overlay_type not in {t.value for t in MastOverlayType}:
            raise ValueError(
                f"Invalid overlay type '{overlay_type}'. "
                f"Must be one of {[t.value for t in MastOverlayType]}."
            )
        super().__init__(overlay_info)

    @property
    def type(self):
        return self.get("type")

    @property
    def options(self):
        return self.get("options")

    @property
    def name(self):
        return self.options.get("name")

    @property
    def data(self):
        ignored = ["type", "options"]
        return {key: value for key, value in self.items() if key not in ignored}

    def update(self, **new_options):
        if not new_options:
            raise ValueError(
                f"Cannot update overlayer `{self.name}` since no options to "
                "update were provided."
            )

        self.app.remove_overlay(self)
        updated_options = {**self.options, **new_options}

        if self.type == MastOverlayType.MARKER.value:
            markers = self.get("update_info")
            overlay_info = self.app.add_markers(markers, **updated_options)
        elif self.type == MastOverlayType.CATALOG.value:
            overlay_info = self.app.add_catalog_from_URL(self["votable_URL"], updated_options)
        elif self.type == MastOverlayType.TABLE.value:
            overlay_info = self.app.add_table(
                self["table"],
                shape=self.options.get("shape", "cross"),
                **updated_options
            )
        elif self.type == MastOverlayType.OVERLAY_REGION.value:
            regions = self["update_info"]
            new_regions = []
            for region in regions:
                style = self.options.copy()
                if "color" in style:
                    style["edgecolor"] = style["color"]
                style.pop("name", None)
                region.visual.update(style)
                new_regions.append(region)
            overlay_info = self.app.add_graphic_overlay_from_region(regions, **updated_options)
        elif self.type == MastOverlayType.OVERLAY_STCS.value:
            update_info = self["update_info"]
            overlay_info = self.app.add_graphic_overlay_from_stcs(update_info, **updated_options)

        return overlay_info
