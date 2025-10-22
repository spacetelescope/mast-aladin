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

opened_sidecars = []
default_height = 500


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


class AppSidecar:
    loaded_apps = []
    _sidecar_context = None

    @classmethod
    def open(
        cls,
        *apps,
        anchor='split-bottom',
        use_current_apps=False,
        title='mast-aladin & jdaviz',
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
        anchor : str, optional (default is `'split-bottom'`)
            One of the anchor location options available from
            ``jupyterlab-sidecar``, which include:

                {'split-right', 'split-left', 'split-top',
                 'split-bottom', 'tab-before', 'tab-after',
                 'right'}

        use_current_apps : bool, optional (default is `False`)
            If `True`, get the last constructed Imviz and
            mast-aladin instances to open in the sidecar

        title : str, optional (default is 'mast-aladin & jdaviz')
            Title to appear in the tab label for the sidecar in
            jupyterlab.

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
        self = cls()

        # This must be run first because we don't have the ability to close multiple
        # sidecars without possibly closing all widgets
        if close_existing:
            cls.close_all()

        apps = list(apps)

        if not len(apps):
            # if no apps are given, include one of each:
            include_jdaviz = include_aladin = True

        mal_instances = [app for app in apps if is_aladin(app)]
        jdaviz_instances = []

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

        n_columns = len(apps)

        if not n_columns:
            raise ValueError("No apps to show in sidecar.")

        self.loaded_apps = apps

        @solara.component
        def SidecarContents(n_columns=n_columns):
            style = f"height={height} !important;"

            with solara.Columns(n_columns * [1], gutters_dense=True) as main:
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

        self._sidecar_context = UpstreamSidecar(anchor=anchor, title=title)
        self._sidecar_context.layout.height = "100% !important;"
        with self._sidecar_context:
            solara.display(SidecarContents())

        opened_sidecars.append(self)
        return tuple(apps)

    def close(self):
        """
        Close this particular `sidecar` instance.
        """
        # close jdaviz apps within the sidecar:
        for app in self.loaded_apps:
            if is_jdaviz(app):
                app.app.close()

        # now close sidecar(s):
        if self._sidecar_context is not None:
            self._sidecar_context.close()

    @classmethod
    def close_all(cls):
        """
        Close all `sidecar` instances.
        """
        while len(opened_sidecars):
            sidecar = opened_sidecars.pop()
            sidecar.close()

    @staticmethod
    def resize_all(height=default_height):
        """
        Resize all opened sidecars with ``height`` in pixels.
        """
        for sc in opened_sidecars:
            for app in sc.loaded_apps:
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

    else:
        warnings.warn(
            f"height could not be set for unrecognized app: {app}",
            UserWarning
        )
