<template>
  <v-container
    fluid
    id="column_selection"
  >
    <v-row
      align="end"
      no-gutters
    >
      <v-col cols="6">
        <v-label>{{ title }}</v-label>
      </v-col>
      <v-col
        cols="6"
        class="text-right"
      >
        <v-btn
          class="select-all-btn"
          :disabled="disabled"
          size="small"
          aria-label="Select all columns"
          @click="select_all"
        >
          <v-icon size="small">mdi-checkbox-multiple-marked</v-icon>
        </v-btn>
        <v-btn
          class="select-none-btn ml-1"
          :disabled="disabled"
          size="small"
          aria-label="Select no columns"
          @click="select_none"
        >
          <v-icon size="small">mdi-checkbox-multiple-blank-outline</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12">
        <v-autocomplete
          v-model="selected_columns"
          :items="column_items"
          :disabled="disabled"
          item-title="title"
          item-value="value"
          :label="label"
          multiple
          chips
          closable-chips
          :chip-props="{ label: true, closeIcon: 'mdi-close-box' }"
          clearable
          variant="outlined"
          hide-details
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<style>
#column_selection {
  color-scheme: light dark;
}

#column_selection .v-label {
  color: light-dark(#013b4d, #b4dbe9);
  font-weight: 900;
}

#column_selection .select-all-btn,
#column_selection .select-none-btn {
  background-color: #013b4d;
  color: white;
  font-weight: 900;
}

#column_selection .v-chip {
  background-color: light-dark(#b4dbe8, #013b4d);
  color: light-dark(black, white);
  font-weight: 900;
}

#column_selection .select-all-btn:hover,
#column_selection .select-none-btn:hover,
#column_selection .option-btn:hover,
#column_selection .v-chip:hover,
#column_selection .v-autocomplete .v-input__icon--clear:hover,
#column_selection .v-autocomplete .v-input__slot:hover
#column_selection .v-list-item:hover {

  background-color: #FF9D42 !important;
}
</style>
