import ipyvuetify as v
import traitlets


class SourceSelector(v.VuetifyTemplate):
    template_file = __file__, "source_selector.vue"

    selected_column = traitlets.Unicode(allow_none=True).tag(sync=True)
    columns = traitlets.List(traitlets.Unicode(), default_value=[]).tag(sync=True)
    column_items = traitlets.List(traitlets.Dict(), default_value=[]).tag(sync=True)
    disabled_columns = traitlets.List(traitlets.Unicode(), default_value=[]).tag(sync=True)
    title = traitlets.Unicode(default_value="Select Column").tag(sync=True)
    description = traitlets.Unicode(default_value="").tag(sync=True)
    label = traitlets.Unicode(default_value="Choose column").tag(sync=True)

    def __init__(self, columns, selected_column=None, **kwargs):
        super().__init__(**kwargs)
        self.columns = columns
        self.selected_column = selected_column

        self.title = "Source widget"
        self.description = "The widget whose current viewport settings control the synchronized view."  # noqa: E501
        self.label = "source ="

    @traitlets.observe("columns")
    def _update_column_items(self, change):
        self.column_items = [
            {
                "title": column,
                "value": column,
            }
            for column in change["new"]
            if column not in self.disabled_columns
        ]
        if self.selected_column not in self.columns:
            self.selected_column = None

    @traitlets.observe("disabled_columns")
    def _update_disabled_columns(self, change):
        self.column_items = [
            {
                "title": column,
                "value": column,
            }
            for column in self.columns
            if column not in change["new"]
        ]
        if self.selected_column in self.disabled_columns:
            self.selected_column = None

    def set_disabled_columns(self, *columns):
        self.disabled_columns = list(columns)
