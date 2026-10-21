import ipyvuetify as v
import traitlets


class Switch(v.VuetifyTemplate):
    template_file = __file__, "switch.vue"
    value = traitlets.Unicode(default_value="Sync").tag(sync=True)
    disabled = traitlets.Bool(default_value=True).tag(sync=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
