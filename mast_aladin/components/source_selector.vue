<template>
  <v-container
    fluid
    id="source_selector"
    class="viewer-sync-selector"
  >
    <v-row
        align="end"
        no-gutters
      >
        <v-col cols="6">
          <v-label class="widget-title">{{ title }}</v-label>
        </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12">
        <v-autocomplete
          v-model="selected_column"
          :items="column_items"
          item-title="title"
          item-value="value"
          :label="label"
          variant="outlined"
          hide-details
          :menu-props="{ attach: '#source_selector' }"
          rounded="0" 
          density="compact"
          :description="description"
          v-tooltip:top="{ text: description, openDelay: 1000, contentClass: 'tooltip' }"
        />
      </v-col>
    </v-row>
  </v-container>
</template>