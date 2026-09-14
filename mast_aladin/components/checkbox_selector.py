import ipyvuetify as v
import traitlets


class CheckboxSelector(v.VuetifyTemplate):
    template_file = __file__, "checkbox_selector.vue"

    options = traitlets.List(traitlets.Unicode(), default_value=[]).tag(sync=True)
    option_items = traitlets.List(traitlets.Dict(), default_value=[]).tag(sync=True)
    selected = traitlets.List(traitlets.Unicode(), default_value=[]).tag(sync=True)
    title = traitlets.Unicode(default_value="Title").tag(sync=True)
    label = traitlets.Unicode(default_value="Select").tag(sync=True)

    def __init__(self, options, title=None, label=None, **kwargs):
        super().__init__(**kwargs)

        self.options = options
        self.selected = options  # Default to all options selected
        if title:
            self.title = title
        if label:
            self.label = label

    @traitlets.observe("options")
    def _update_column_items(self, change):
        self.option_items = [
            {
                "title": option,
                "value": option,
            }
            for option in change["new"]
        ]
        self.selected = [name for name in self.selected if name in self.options]

    def vue_select_all(self, data=None):
        self.selected = self.options

    def vue_select_none(self, data=None):
        self.selected = []
