import solara
import warnings
from ipyaladin import Aladin
from sidecar import Sidecar as UpstreamSidecar
from mast_table import MastTable
from mast_aladin.app import MastAladin, gca

try:
    from jdaviz.core.helpers import ConfigHelper
except ImportError:
    ConfigHelper = None

default_height = 500
default_anchor = 'split-right'


def is_jdaviz(app):
    """
    If jdaviz can be imported, check app is instanace of ConfigHelper;
    otherwise you can't have a jdaviz app:
    """
    if ConfigHelper is not None:
        return isinstance(app, ConfigHelper)

    return False


def is_aladin(app):
    return isinstance(app, Aladin)


class AppSidecarManager:
    _sidecar_context = None
    _jdaviz_counter = 0
    _aladin_counter = 0
    _other_counter = 0

    def __init__(self):
        self.loaded_apps = []

    def open(
        self,
        *apps,
        anchor='split-bottom',
        use_current_apps=False,
        titles=None,
        include_aladin=False,
        include_jdaviz=False,
        close_existing=True,
        height=default_height,
    ):

        """
        Open ``apps`` in a sidecar [1]_. If none are given and
        ``include_aladin`` and ``include_jdaviz`` are `True`,
        open a sidecar with one of each.

        Parameters
        ----------
        anchor : str or list of str, optional (default: 'split-bottom')
            One or more of the anchor location options available from
            ``jupyterlab-sidecar``, which include:

                {'split-right', 'split-left', 'split-top',
                 'split-bottom', 'tab-before', 'tab-after',
                 'right'}

            - If a single anchor is provided, all apps share the same sidecar.
            - If multiple anchors are provided, each app is launched in its
            own sidecar relative to the previous app's sidecar.
            - If there are fewer anchors than apps, remaining apps default to
            'split-right'.

        use_current_apps : bool, optional (default is `False`)
            If `True`, get the last constructed Imviz and
            mast-aladin instances to open in the sidecar

        titles : list of str, or None, optional (default is `None`)
            Title to appear in the tab label for each sidecar in
            jupyterlab. If `None`, label sidecars sequentially wit
            "Sidecar 0", "Sidecar 1", etc.

        include_aladin : bool, optional (default is `False`)
            The sidecar must include at least one
            mast-aladin instance. If none are already
            available, a new one will be created.

        include_jdaviz : bool, optional (default is `False`)
            The sidecar must include at least one
            jdaviz instance. If none are already available,
            a new one will be created.

        close_existing : bool, optional (default is `True`)
            Close existing sidecar(s) before opening a new one.

        References
        ----------
        .. [1] https://github.com/jupyter-widgets/jupyterlab-sidecar
        """
        # initialize the object here:
        # This must be run first because we don't have the ability to close multiple
        # sidecars without possibly closing all widgets
        if close_existing:
            self.close_all()

        apps, default_titles = self._resolve_apps(
            apps, include_aladin, include_jdaviz, use_current_apps
        )

        if titles is None:
            titles = default_titles

        if not apps:
            raise ValueError("No apps to show in sidecar.")

        self.loaded_apps = apps

        self._attach_sidecars(apps, anchor, titles)

        self._display_sidecar_contents(apps, height)

        self.loaded_apps += apps
        return tuple(apps)

    def _resolve_apps(self, apps, include_aladin, include_jdaviz, use_current_apps):
        """
        Ensure requested apps exist, creating or reusing as needed.
        """
        apps = list(apps)

        if not len(apps) and not include_aladin and not include_jdaviz:
            # if no apps are given, include one of each:
            include_jdaviz = include_aladin = True

        mal_instances = [app for app in apps if is_aladin(app)]
        jdaviz_instances = [app for app in apps if is_jdaviz(app)]

        if not len(mal_instances) and include_aladin:
            mal = gca()
            if not use_current_apps or (use_current_apps and mal is None):
                mal = MastAladin()
            apps.append(mal)

        try:
            from jdaviz.configs.imviz.helper import Imviz, _current_app as viz

            jdaviz_instances = [app for app in apps if is_jdaviz(app)]

            # construct new imviz if not using current app or no current app exists:
            if not len(jdaviz_instances) and include_jdaviz:
                if not use_current_apps or (use_current_apps and viz is None):
                    viz = Imviz()
                apps.append(viz)

        except ImportError:
            warnings.warn(
                "`AppSidecar` found that jdaviz was not installed. To install it, "
                "run `pip install jdaviz`.",
                UserWarning
            )

        default_titles = []
        for app in apps:
            if is_jdaviz(app):
                default_titles.append(
                    "jdaviz" + (f" ({self._jdaviz_counter})" if self._jdaviz_counter else '')
                )
                self._jdaviz_counter += 1
            elif is_aladin(app):
                default_titles.append(
                    "mast-aladin" + (f" ({self._aladin_counter})" if self._aladin_counter else '')
                )
                self._aladin_counter += 1
            else:
                default_titles.append(
                    "Sidecar" + (f" ({self._other_counter})" if self._other_counter else '')
                )
                self._other_counter += 1
        return apps, default_titles

    def _attach_sidecars(self, apps, anchor, titles):
        """
        Attach apps to sidecars. If only one anchor, all apps share
        a single sidecar. Otherwise, create one sidecar per app.
        In the multiple case, each sidecar `n` will reference the
        `n-1` sidecar instance.
        """
        if not isinstance(anchor, list):
            anchor = [anchor]

        if len(anchor) == 1:
            # shared single sidecar
            ctx = UpstreamSidecar(anchor=anchor[0], title=titles[0])
            for app in apps:
                app.sidecar = ctx

        else:
            # multiple sidecars
            anchor = self._normalize_anchor(anchor, apps)
            ref = None
            for app, anc, title in zip(apps, anchor, titles):
                ctx = UpstreamSidecar(anchor=anc, title=title, ref=ref)
                app.sidecar = ctx
                ref = ctx

    def _normalize_anchor(self, anchor, apps):
        """
        Ensure anchor is a list of correct length
        """
        n_apps = len(apps)
        n_anchors = len(anchor)

        if n_anchors < n_apps:
            warnings.warn(
                f"Anchors must either be a single value or one per app. "
                f"Filling missing anchors with `{default_anchor}`."
            )

            return anchor + [default_anchor] * (n_apps-n_anchors)
        return anchor

    def _display_sidecar_contents(self, apps, height):
        @solara.component
        def SidecarContents(apps):
            style = f"height={height} !important;"

            with solara.Columns(len(apps) * [1], gutters_dense=True) as main:
                for app in apps:

                    if is_aladin(app):
                        # MastAladin:
                        with solara.Column(gap='0px', style=style):
                            solara.display(app)

                    elif is_jdaviz(app):
                        # jdaviz:
                        with solara.Column(gap='0px', style=style):
                            solara.display(app.app)

                    else:
                        # other:
                        with solara.Column(gap='0px'):
                            solara.display(app)

                    set_app_height(app, height)

            return main

        for app in apps:
            with app.sidecar:
                solara.display(SidecarContents(apps=[app]))

    def close_all(self):
        """
        Close this particular `sidecar` instance.
        """
        for app in self.loaded_apps:
            # close jdaviz apps within the sidecar:
            if is_jdaviz(app):
                app.app.close()

            # now close sidecar(s):
            if app.sidecar is not None:
                app.sidecar.close()
        self.loaded_apps = []

    def resize_all(self, height=default_height):
        """
        Resize all opened sidecars with ``height`` in pixels.
        """
        for app in self.loaded_apps:
            set_app_height(app, height)


def set_app_height(app, height):
    """
    For an app instance ``app``, set the app height to be
    ``height`` pixels. ``height`` may be an integer in units
    of pixels, or "100%".
    """
    if is_jdaviz(app):
        if isinstance(height, int):
            height = f"{height}px"

        app.app.layout.height = height
        app.app.state.settings['context']['notebook']['max_height'] = height

    elif is_aladin(app):
        if height == '100%':
            app.height = -1
        elif isinstance(height, int):
            app.height = height

    elif isinstance(app, MastTable):
        if isinstance(height, int):
            height = f"{height}px"

        app.layout.height = height


AppSidecar = AppSidecarManager()
