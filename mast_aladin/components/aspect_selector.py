import ipyvuetify as v
import traitlets


class AspectSelector(v.VuetifyTemplate):
    template_file = __file__, "aspect_selector.vue"

    options = traitlets.List(traitlets.Unicode(), default_value=[]).tag(sync=True)
    option_items = traitlets.List(traitlets.Dict(), default_value=[]).tag(sync=True)
    selected = traitlets.List(traitlets.Unicode(), default_value=[]).tag(sync=True)
    title = traitlets.Unicode().tag(sync=True)
    label = traitlets.Unicode().tag(sync=True)
    descriptions = traitlets.Dict(
        key_trait=traitlets.Unicode(),
        value_trait=traitlets.Unicode(),
        default_value={},
    ).tag(sync=True)

    def __init__(self, options, descriptions=None, **kwargs):
        super().__init__(**kwargs)

        self.options = options
        self.selected = list(options)  # Default to all options selected
        self.title = "Aspect Selector"
        self.label = "Aspects"
        self.descriptions = descriptions or {}

    @traitlets.observe("options", "descriptions")
    def _update_option_items(self, change):
        self.option_items = [
            {
                "title": option,
                "value": option,
                "description": self.descriptions.get(option, ""),
            }
            for option in self.options
        ]
        self.selected = [
            option for option in self.selected
            if option in self.options
        ]

    def vue_select_all(self, data=None):
        self.selected = self.options

    def vue_select_none(self, data=None):
        self.selected = []
