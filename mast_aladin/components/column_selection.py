import ipyvuetify as v
import traitlets


class ColumnSelection(v.VuetifyTemplate):
    template_file = __file__, "column_selection.vue"

    selected_columns = traitlets.List(traitlets.Unicode(), default_value=[]).tag(sync=True)
    columns = traitlets.List(traitlets.Unicode(), default_value=[]).tag(sync=True)
    column_items = traitlets.List(traitlets.Dict(), default_value=[]).tag(sync=True)
    disabled_columns = traitlets.List(traitlets.Unicode(allow_none=True), default_value=[]).tag(sync=True)  # noqa: E501
    title = traitlets.Unicode().tag(sync=True)
    label = traitlets.Unicode().tag(sync=True)

    def __init__(
        self,
        columns,
        selected_columns=None,
        title="Select Columns",
        label="Choose columns",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.columns = columns
        self.selected_columns = selected_columns or []
        self.disabled_columns = []
        self.title = title
        self.label = label

    def _get_selected_columns(self):
        return [column for column in self.selected_columns if column not in self.disabled_columns]

    def _get_enabled_columns(self):
        return [column for column in self.columns if column not in self.disabled_columns]

    @traitlets.observe("columns")
    def _update_column_items(self, change):
        self.column_items = [
            {
                "title": column,
                "value": column,
            }
            for column in self._get_enabled_columns()
        ]
        self.selected_columns = self._get_selected_columns()

    @traitlets.observe("disabled_columns")
    def _update_disabled_columns(self, change):
        self.column_items = [
            {
                "title": column,
                "value": column,
            }
            for column in self._get_enabled_columns()
        ]
        self.selected_columns = self._get_selected_columns()

    def set_disabled_columns(self, *columns):
        if columns is None:
            columns = []
        if isinstance(columns, str):
            columns = [columns]

        self.disabled_columns = columns

    def vue_select_all(self, data=None):
        self.selected_columns = [
            column for column in self.columns if column not in self.disabled_columns
        ]

    def vue_select_none(self, data=None):
        self.selected_columns = []
