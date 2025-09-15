<template>
  <div v-if="show_if_empty || items.length">
  <v-container fluid>
    <v-row class="text-right">
      <v-col style="max-width: 400px;">
      <div class="row-select">
        <v-select
          class="no-hint"
          v-model="headers_visible"
          :items="headers_avail"
          @change="$emit('update:headers_visible', $event)"
          label="Display columns"
          multiple
          dense
        >
        <template v-slot:selection="{ item, index }">
          <span
            v-if="index === 0"
            class="grey--text text-caption"
          >
            ({{ headers_visible.length}} selected)
          </span>
        </template>
        <template v-slot:prepend-item>
          <v-list-item
            ripple
            @mousedown.prevent
            @click="() => {if (headers_visible.length < headers_avail.length) { headers_visible = headers_avail} else {headers_visible = []}}"
          >
            <v-list-item-action>
              <v-icon>
                {{ headers_visible.length == headers_avail.length ? 'mdi-close-box' : headers_visible.length ? 'mdi-minus-box' : 'mdi-checkbox-blank-outline' }}
              </v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>
                {{ headers_visible.length < headers_avail.length ? "Select All" : "Clear All" }}
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-divider class="mt-2"></v-divider>
        </template>
        </v-select>
      </div>
      </v-col>

      <v-col>
        <jupyter-widget :widget="popout_button"></jupyter-widget>

        <v-menu v-model="menu_open" :close-on-content-click="false" anchor="start end">
          <template v-slot:activator="{ on }">
            <v-btn v-on="on" icon><v-icon>mdi-menu</v-icon></v-btn>
          </template>

          <v-card min-width="300">
            <v-list>
              <v-list-item>
                <v-switch v-model="show_tooltips" color="rgb(0, 97, 126)" label="Show column definition on hover"></v-switch>
              </v-list-item>
            </v-list>
          </v-card>

        </v-menu>
      </v-col>
    </v-row>
    <v-row>
      <v-container fluid>
      <div class="table-component" style="padding: 5px;">
      <v-data-table
        dense
        :headers="headers_visible_sorted_description"
        :items="items"
        :item-key="item_key"
        :show-select="show_rowselect"
        :single-select="!multiselect"
        :items-per-page="items_per_page"
        v-model="selected_rows"
        class="elevation-2"
      >
      <template v-for="h in headers_visible_sorted_description" v-slot:[`header.${h.value}`]="{ header }">
        <div style="color: white;">
          <div v-if="show_tooltips">
            <v-tooltip top>
              <template v-slot:activator="{ on }">              
                <span v-on="on"><strong>{{h.name}}</strong></span>
              </template>
                <p style="width: 300px">
                  <strong>{{h.name}}</strong>: {{h.description}}
                </p>
            </v-tooltip>
          </div>
          <div v-else>
              <span><strong>{{h.name}}</strong></span>
          </div>
        </div>
      </template>
      </v-data-table>
      </div>
      </v-container>
    </v-row>
    <div v-if="selected_rows.length > 0 && enable_load_in_app">
      <v-row>
      <v-col align="right">
          <v-label>Open products in:</v-label>
          <v-btn @click="open_selected_rows_in_aladin"><v-label>aladin</v-label></v-btn>
          <v-btn @click="open_selected_rows_in_jdaviz"><v-label>jdaviz</v-label></v-btn>
      </v-col>
      </v-row>
    </div>
    </v-container>
</div>
</template>

<script>
module.exports = {
  props: ['column_descriptions', 'show_tooltips', 'popout_button'],
  computed: {
    headers_visible_sorted() {
      return this.headers_avail.filter(item => this.headers_visible.indexOf(item) !== -1);
    },
    headers_visible_sorted_description() {
      return this.headers_visible_sorted.map(item => {
        return {'name': item, 'value': item, 'description': this.get_header_description(item)}
      });
    }

  },
  methods: {
    get_header_description(item) {
      entry = this.column_descriptions.find(entry => entry.name == item)
      return entry !== undefined ? entry.description : null;
    }
  }
};
</script>


<style scoped>
.table-component {
  thead {
      background-color: rgb(0, 97, 126); /* MAST button background lighter-blue color */
    }
}
.v-tooltip__content {
  opacity: 1 !important;
}
</style>