<template>
  <v-container
    fluid
    id="column_selection"
  >
    <v-row
      align="end"
      no-gutters
      class="header-row"
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
          size="x-small"
          aria-label="Select all columns"
          @click="select_all"
          rounded="0"
        >
          <v-icon size="small">mdi-checkbox-multiple-marked</v-icon>
        </v-btn>
        <v-btn
          class="select-none-btn ml-1"
          :disabled="disabled"
          size="x-small"
          aria-label="Select no columns"
          @click="select_none"
          rounded="0"
        >
          <v-icon size="small">mdi-checkbox-multiple-blank-outline</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12">
        <v-autocomplete
          v-model="selected_columns"
          class="column-autocomplete"
          :items="column_items"
          item-title="title"
          item-value="value"
          :label="label"
          multiple
          chips
          closable-chips
          variant="outlined"
          hide-details
          :menu-props="{ attach: '#column_selection' }"
          rounded="0"
          density="compact"
        >
          <template #chip="{ item, index, props }">
            <v-chip
              v-bind="props"
              :model-value="item.selected"
              :data-column-name="item.raw.column_name"
              label
              variant="elevated"
              closable
              close-icon="mdi-close-box"
              @click="item.select"
              @click:close="remove(item.raw)"
              rounded="0" 
            />
          </template>
        </v-autocomplete>
      </v-col>
    </v-row>
  </v-container>
</template>

<style>
#column_selection .v-label {
  color: light-dark(#013b4d, #b4dbe9);
  font-weight: 900;
  opacity: 1;
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
#column_selection .v-autocomplete .v-input__icon--clear:hover,
#column_selection .v-autocomplete .v-input__slot:hover,
#column_selection .v-menu__content .v-list-item:hover {

  background-color: #FF9D42;
}

#column_selection .v-combobox--chips .v-combobox__selection,
#column_selection .v-autocomplete--chips .v-autocomplete__selection {
  margin: 4px;
}

#column_selection .v-list .v-list-item--link:not(.v-list-item--prepend):hover,
#column_selection .v-list .v-list-item--link:not(.v-list-item--prepend):focus,
#column_selection .v-list .v-list-item--active:not(.v-list-item--prepend):focus
{
  /* List item hover */
  background-color: light-dark(#FF9D42, #A75000);
}

#column_selection .v-list .v-list-item--active:not(.v-list-item--prepend) {
  /* List item, active item */
  background-color: light-dark(#C6F0FD, #00617E);
  opacity: 1;
}

#column_selection .v-icon--clickable:not(.v-data-table-header__sort-icon):hover,
#column_selection .v-icon--clickable:not(.v-data-table-header__sort-icon):focus {
  color: light-dark(#FF9D42, #A75000);
}

#column_selection .mdi-close-box:hover,
#column_selection .mdi-close-box:focus {
  color: #A75000;
}

#column_selection .v-chip--selected, .v-chip--active {
  box-shadow: none;
}

#column_selection .v-autocomplete--chips .v-autocomplete__selection {
  margin: 4px;
}

#column_selection .v-field--variant-outlined .v-field__outline__start,
#column_selection .v-field--variant-outlined .v-field__outline__notch::after,
#column_selection .v-field--variant-outlined .v-field__outline__end {
  /* v-autocomplete outline border color */
  color: light-dark(black, white);
  opacity: 1;
}

#column_selection .v-field--variant-outlined:not(.v-field--active) .v-field__outline__notch::before {
  /* only force full opacity while the label is resting; leave it alone when
     active so vuetify can still cut the notch gap for the floating label */
  color: light-dark(black, white);
  opacity: 1;
}
</style>
