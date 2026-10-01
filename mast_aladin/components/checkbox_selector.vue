<template>
  <v-container
    fluid
    id="checkbox_selector"
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
              aria-label="Select all"
              @click="select_all"
              rounded="0"
            >
              <v-icon size="small">mdi-checkbox-multiple-marked</v-icon>
            </v-btn>
            <v-btn
              class="select-none-btn ml-1"
              :disabled="disabled"
              size="x-small"
              aria-label="Select none"
              @click="select_none"
              rounded="0"
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
            <template v-for="(option, index) in options" :key="option">
              <v-btn
                :value="option"
                class="option-btn"
              >
                <v-icon size="small" class="mr-1">
                  {{ selected.includes(option) ? 'mdi-checkbox-marked' : 'mdi-checkbox-blank-outline' }}
                </v-icon>
                {{ option }}
              </v-btn>
              <v-divider
                  v-if="index < options.length - 1"
                  class="option-divider border-opacity-100 my-1 mx-0"
                  vertical
                >
                </v-divider>
            </template>
          </v-btn-toggle>
        </v-sheet>
      </div>
    </v-row>
  </v-container>
</template>

<style>
#checkbox_selector .select-all-btn,
#checkbox_selector .select-none-btn {
  background-color: #013b4d;
  color: white;
  font-weight: 900;
}

#checkbox_selector .label-btn {
  color: light-dark(#013b4d, #b4dbe9);
  opacity: 1;
  font-weight: 900;
  letter-spacing: 1.25px;
}

#checkbox_selector .v-label {
  color: light-dark(#013b4d, #b4dbe9);
  font-weight: 900;
  opacity: 1;
}

#checkbox_selector .border {
  color: light-dark(black, white);
}

#checkbox_selector .option-divider {
  color: light-dark(black, white);
}

#checkbox_selector .option-btn {
  background-color: transparent;
  color: light-dark(#013b4d, #b4dbe9);
  font-weight: 900;
  letter-spacing: 1.25px;
}

#checkbox_selector .option-btn.v-btn--active {
  background-color: light-dark(#b4dbe8, #013b4d);
}

#checkbox_selector .select-all-btn:hover,
#checkbox_selector .select-none-btn:hover,
#checkbox_selector .option-btn:hover 
{ 
  background-color: light-dark(#FF9D42, #A75000);
}
</style>