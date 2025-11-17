from datetime import datetime
from echo import delay_callback
from traitlets import Unicode, Bool, Float, observe, HasTraits

from mast_aladin import gca


class ViewportOutline(HasTraits):
    """
    Draw the outline of a mast-aladin viewport's coordinate limits in
    jdaviz, and vice versa.

    On initialization, clears any existing viewport outlines
    in the viewers, before creating new ones.

    Traitlets
    ---------
    outline_color : str
        Hex color code for the outline overlay, default is red.
    outline_width : str
        Width of the outline overlay, default is 4.
    jdaviz_outline_in_aladin : bool
        Draw the outline of the jdaviz viewport in mast-aladin.
        Default is True.
    aladin_outline_in_jdaviz : bool
        Draw the outline of the mast-aladin viewport in jdaviz.
        Default is True.
    """
    aladin_overlay = None
    jdaviz_overlay = None

    outline_color = Unicode('#ff0000').tag(sync=True)
    outline_width = Float(4).tag(sync=True)
    jdaviz_outline_in_aladin = Bool(True).tag(sync=True)
    aladin_outline_in_jdaviz = Bool(True).tag(sync=True)

    def __init__(
            self, jdaviz_viewer, aladin,
            jdaviz_outline_in_aladin=True,
            aladin_outline_in_jdaviz=True,
            clear_existing=True
            ):
        """
        Parameters
        ----------
        jdaviz_viewer : `~jdaviz.configs.imviz.plugins.viewers.ImvizImageView`
            Instance of a jdaviz viewer. The default viewer in Imviz can be
            retrieved from ``imviz_helper.default_viewer``.
        aladin : `~mast_aladin.MastAladin`
            Instance of a Mast Aladin app.
        jdaviz_outline_in_aladin : bool
            Draw the outline of the jdaviz viewport in mast-aladin.
            Default is True.
        aladin_outline_in_jdaviz : bool
            Draw the outline of the mast-aladin viewport in jdaviz.
            Default is True.
        """
        self.jdaviz_viewer = jdaviz_viewer
        self.aladin = aladin
        self.aladin_outline_in_jdaviz = aladin_outline_in_jdaviz
        self.jdaviz_outline_in_aladin = jdaviz_outline_in_aladin

        self._clear_existing_outlines()
        self._update_or_clear_outlines()

    def _clear_jdaviz_outline_in_aladin(self):
        """
        Clear the latest jdaviz viewport outline drawn in aladin.
        """
        if self.aladin_overlay is not None:
            overlay_label = self.aladin_overlay['options']['name']
            if overlay_label in self.aladin._overlays:
                self.aladin.remove_overlay(self.aladin_overlay)

    def _clear_aladin_outline_in_jdaviz(self):
        """
        Clear the latest mast-aladin viewport outline drawn in jdaviz.
        """
        if self.jdaviz_overlay is not None:
            glue_viewer = self.jdaviz_viewer._obj.glue_viewer
            overlay_label = self.jdaviz_overlay['region_label']
            if overlay_label in glue_viewer._get_region_overlay_labels():
                glue_viewer._remove_region_overlay(overlay_label)

    def _update_jdaviz_outline_in_aladin(self, msg={}):
        """
        Update the jdaviz viewport outline drawn in aladin.
        """
        self._clear_jdaviz_outline_in_aladin()

        imviz_viewport = self.jdaviz_viewer.get_viewport_region()
        self.aladin_overlay = self.aladin.add_graphic_overlay_from_region(
            imviz_viewport,
            name=self._viewport_label(app_name='jdaviz'),
            color=self.outline_color,
            lineWidth=self.outline_width,
        )

    def _update_aladin_outline_in_jdaviz(self, msg={}):
        """
        Update the mast-aladin viewport outline drawn in jdaviz.
        """
        self._clear_aladin_outline_in_jdaviz()

        # it's possible that this method has been called before the
        # aladin instance has been rendered. Check, and raise an error
        # if aladin hasn't been rendered yet.
        if not self.aladin._wcs:
            raise ValueError(
                f"{self.aladin} is not yet rendered. Viewport outlines "
                "cannot be initialized until mast-aladin has been rendered "
                "in the Jupyter environment."
            )

        self.jdaviz_overlay = dict(
            region=self.aladin.get_viewport_region(),
            region_label=self._viewport_label(app_name='mast-aladin'),
            colors=[self.outline_color],
            stroke_width=self.outline_width,
        )
        glue_viewer = self.jdaviz_viewer._obj.glue_viewer
        glue_viewer._add_region_overlay(**self.jdaviz_overlay)

    def _viewport_label(self, app_name=None):
        """
        Generate a label for the viewport outline overlay layers.
        """
        # hours, minutes, seconds:
        time = datetime.now().time().strftime('%H:%M:%S')
        return (
            ('' if app_name is None else f"{app_name} @ ") + time
        )

    @observe('jdaviz_outline_in_aladin', 'aladin_outline_in_jdaviz')
    def _update_or_clear_outlines(self, msg={}):
        """
        Update requested or existing outlines, and clear others.
        """
        if self.aladin_outline_in_jdaviz:
            # add jdaviz viewport overlay in mast-aladin
            self._update_aladin_outline_in_jdaviz()

            # observe mast-aladin traitlets to trigger updates in jdaviz:
            self.aladin.observe(self._update_aladin_outline_in_jdaviz, '_fov')
            self.aladin.observe(self._update_aladin_outline_in_jdaviz, '_target')
        else:
            self._clear_aladin_outline_in_jdaviz()

        if self.jdaviz_outline_in_aladin:
            self._update_jdaviz_outline_in_aladin()
            glue_viewer = self.jdaviz_viewer._obj.glue_viewer

            # add callback to jdaviz viewerport limits to trigger updates in mast-aladin
            glue_viewer.state.add_callback(
                'x_min', self._update_jdaviz_outline_in_aladin
            )

        else:
            self._clear_jdaviz_outline_in_aladin()

    @observe('outline_color', 'outline_width')
    def _redraw(self, msg={}):
        """
        Force an udpate on the overlays
        """
        if self.aladin_outline_in_jdaviz:
            self._update_aladin_outline_in_jdaviz()
        if self.jdaviz_outline_in_aladin:
            self._update_jdaviz_outline_in_aladin()

    def clear_all(self):
        """
        Clear all outlines, including those that were created by another
        instance of ``ViewportOutline``.
        """
        with delay_callback('jdaviz_outline_in_aladin', 'aladin_outline_in_jdaviz'):
            self.jdaviz_outline_in_aladin = False
            self.aladin_outline_in_jdaviz = False

        self._clear_existing_outlines()

    def _clear_existing_outlines(self):
        """
        Find and remove existing outlines drawn by any instance of `ViewportOutline`.
        """
        aladin_overlays_to_remove = [
            overlay_name for overlay_name in self.aladin.overlays
            if overlay_name.startswith('jdaviz @')
        ]
        self.aladin.remove_overlay(aladin_overlays_to_remove)

        glue_viewer = self.jdaviz_viewer._obj.glue_viewer
        jdaviz_overlays = glue_viewer._get_region_overlay_labels()
        jdaviz_overlays_to_remove = [
            overlay_name for overlay_name in jdaviz_overlays
            if overlay_name.startswith('mast-aladin @')
        ]
        glue_viewer._remove_region_overlay(jdaviz_overlays_to_remove)

    @classmethod
    def for_current_apps(cls, jdaviz_viewer_name=None):
        """
        Construct a ``ViewportOutline`` for the latest instantiated
        instances of `mast_aladin.MastAladin` and
        `~jdaviz.configs.imviz.plugins.viewers.ImvizImageView`.

        Parameters
        ----------
        jdaviz_viewer_name : str or None
            Name for one viewer in jdaviz.
            Two viewport instances. Currently supports only an iterable of two inputs:
            `mast_aladin.MastAladin`, and
            `~jdaviz.configs.imviz.plugins.viewers.ImvizImageView`.
        """
        try:
            from jdaviz.configs.imviz.helper import _current_app as current_jdaviz_app
        except ImportError:
            current_jdaviz_app = None

        if not current_jdaviz_app:
            raise ValueError("No available jdaviz instance found.")

        mast_aladin = gca()

        if jdaviz_viewer_name is None:
            # todo: this will need updates for deconfigged:
            jdaviz_viewer_name = 'imviz-0'

        jdaviz_viewer = current_jdaviz_app.viewers[jdaviz_viewer_name]

        return cls(jdaviz_viewer, mast_aladin)
