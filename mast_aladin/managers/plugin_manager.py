import ipywidgets as widgets
from mast_aladin.plugins import ViewerSync
from IPython.display import display


class PluginManager():
    def __init__(self, mast_manager):
        self._plugins = {
            "viewer_sync": ViewerSync(mast_manager.AppManager),
        }

    def close(self):
        for plugin in self._plugins.values():
            plugin.close()

    @property
    def plugins(self):
        return self._plugins

    def display_plugin(self, id):
        self._plugins[id].display()

    def display(self):
        tab_titles = [key for key in self._plugins]
        children = [plugin.ui for plugin in self._plugins.values()]
        tab = widgets.Tab(
            children=children,
            titles=tab_titles
        )
        display(tab)
