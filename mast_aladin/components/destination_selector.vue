<template>
  <v-container
    fluid
    id="destination_selection"
    class="viewer-sync-selector"
  >
    <v-row
      align="end"
      no-gutters
      class="header-row"
    >
      <v-col cols="6">
        <v-label class="widget-title">{{ title }}</v-label>
      </v-col>
      <v-col
        cols="6"
        class="text-right"
      >
        <v-btn
          class="select-all-btn"
          :disabled="disabled"
          size="x-small"
          aria-label="Select all destination widgets"
          @click="select_all"
          rounded="0"
          v-tooltip:top="{ text: 'Select all destination widgets.', openDelay: 1000, contentClass: 'tooltip' }"
        >
          <v-icon size="small">mdi-checkbox-multiple-marked</v-icon>
        </v-btn>
        <v-btn
          class="select-none-btn"
          :disabled="disabled"
          size="x-small"
          aria-label="Deselect all destination widgets"
          @click="select_none"
          rounded="0"
          v-tooltip:top="{ text: 'Deselect all destination widgets.', openDelay: 1000, contentClass: 'tooltip' }"
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
          :menu-props="{ attach: '#destination_selection' }"
          rounded="0"
          density="compact"
          :description="description"
          v-tooltip:top="{ text: description, openDelay: 1000, contentClass: 'tooltip' }"
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