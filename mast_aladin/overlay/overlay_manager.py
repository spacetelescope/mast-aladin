import warnings
from mast_aladin.overlay.mast_overlay import MastOverlay


class OverlayManager:
    def __init__(self, mast_aladin):
        self.app = mast_aladin
        self._overlays_dict = {}

    def __setitem__(self, key, value):
        self._overlays_dict[key] = value

    def __getitem__(self, key):
        return self._overlays_dict[key]

    def __contains__(self, key):
        return key in self._overlays_dict

    def items(self):
        return self._overlays_dict.items()

    def pop(self, key):
        self._overlays_dict.pop(key)

    def keys(self):
        return self._overlays_dict.keys()

    def make_unique_name(self, name):
        """Create a unique layer name.

        Parameters
        ----------
        name : str
            The current name of the layer to be added to the widget.

        Returns
        -------
        unique_name
            A string that is a unique name for the layer being added.
        """
        unique_name = name
        i = 1

        while unique_name in self._overlays_dict:
            unique_name = f"{name}_{i}"
            i += 1

        return unique_name

    def common_overlay_handling(self, overlay_options, default_name):
        """Handle common functionality across added overlay methods.

        Parameters
        ----------
        overlay_options : dict
            The dictionary of overlay options for the layer being added to the widget.
        default_name : str
            The default name of the overlay being added.

        Returns
        -------
        overlay_options
            The updated dictionary of overlay options for the layer being added
            to the widget.
        """
        name = overlay_options.get("name", default_name)
        unique_name = self.make_unique_name(name=name)
        overlay_options["name"] = unique_name

        if unique_name != name and name != default_name:
            warnings.warn(
                f"Overlayer name `{name}` is already in use. Name `{unique_name}` "
                "will be used instead.",
                stacklevel=2,
            )

        return overlay_options

    def add_overlay(self, overlay_info):
        """Add overlay to overlay dictionary.

        Parameters
        ----------
        overlay_info : dict
            The dictionary of overlay info for the layer being added to the widget.
            Includes overlay options and specific overlay info (URLs, coords, etc.).

        Returns
        -------
        overlay_info
            The overlay options for the layer being added to the widget.
        """

        overlay_info = MastOverlay(overlay_info, self.app)

        self[overlay_info["options"]["name"]] = overlay_info

        return overlay_info
