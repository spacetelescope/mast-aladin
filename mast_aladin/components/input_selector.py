import ipyvuetify as v
import traitlets


class InputSelector(v.VuetifyTemplate):
    template_file = __file__, "input_selector.vue"

    selected_column = traitlets.Unicode(allow_none=True).tag(sync=True)
    columns = traitlets.List(traitlets.Unicode(), default_value=[]).tag(sync=True)
    column_items = traitlets.List(traitlets.Dict(), default_value=[]).tag(sync=True)
    disabled = traitlets.Bool(default_value=False).tag(sync=True)
    title = traitlets.Unicode(default_value="Select Column").tag(sync=True)
    label = traitlets.Unicode(default_value="Choose column").tag(sync=True)

    def __init__(self, columns, selected_column=None, title=None, label=None, **kwargs):
        super().__init__(**kwargs)
        self.columns = columns
        self.selected_column = selected_column or ''

        if title:
            self.title = title
        if label:
            self.label = label

    @traitlets.observe("columns")
    def _update_column_items(self, change):
        self.column_items = [
            {
                "title": column,
                "value": column,
            }
            for column in change["new"]
        ]
        if self.selected_column not in self.columns:
            self.selected_column = ''
