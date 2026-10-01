<template>
  <v-container
    fluid
    id="aspect_selector"
    class="viewer-sync-selector"
  >
    <v-row
      no-gutters
    >
      <div class="flex-shrink-1">
        <v-row
          align="end"
          no-gutters
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
              aria-label="Select all available aspects"
              @click="select_all"
              rounded="0"
              v-tooltip:top="{ text: 'Select all available aspects', openDelay: 1000, contentClass: 'tooltip' }"
            >
              <v-icon size="small">mdi-checkbox-multiple-marked</v-icon>
            </v-btn>
            <v-btn
              class="select-none-btn"
              :disabled="disabled"
              size="x-small"
              aria-label="Unselect all aspects"
              @click="select_none"
              rounded="0"
              v-tooltip:top="{ text: 'Unselect all selected aspects', openDelay: 1000, contentClass: 'tooltip' }"
            >
              <v-icon size="small">mdi-checkbox-multiple-blank-outline</v-icon>
            </v-btn>
          </v-col>
        </v-row>
        <v-sheet
          border
          class="transparent-background border-opacity-100"
        >
          <v-btn-toggle
            v-model="selected"
            multiple
            variant="flat"
            rounded="0"
            density="compact"
          >
            <v-btn 
              disabled
              class="label-btn"
              variant="text"
            >
              {{ label }} =
            </v-btn>
            <template v-for="(option, index) in option_items" :key="option.value">
              <v-btn
                v-bind="props"
                :value="option.value"
                class="option-btn"
                v-tooltip:top="{ text: option.description, openDelay: 1000, contentClass: 'tooltip' }"
              >
                <v-icon size="small" class="mr-1">
                  {{ selected.includes(option.value) ? 'mdi-checkbox-marked' : 'mdi-checkbox-blank-outline' }}
                </v-icon>
                {{ option.title }}
              </v-btn>
              <v-divider
                v-if="index < option_items.length - 1"
                class="option-divider border-opacity-100 my-1 mx-0"
                vertical
              />
          </template>
          </v-btn-toggle>
        </v-sheet>
      </div>
    </v-row>
  </v-container>
</template>