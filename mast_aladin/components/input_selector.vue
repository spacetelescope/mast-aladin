<template>
  <v-container
    fluid
    id="input_selector"
  >
    <v-row
        align="end"
        no-gutters
      >
        <v-col cols="6">
          <v-label>{{ title }}</v-label>
        </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12">
        <v-autocomplete
          v-model="selected_column"
          :items="column_items"
          :disabled="disabled"
          item-title="title"
          item-value="value"
          :label="label"
          clearable
          variant="outlined"
          hide-details
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<style>
#input_selector {
  color-scheme: light dark;
}

#input_selector .v-label {
  color: light-dark(#013b4d, #b4dbe9);
  font-weight: 900;
}
</style>