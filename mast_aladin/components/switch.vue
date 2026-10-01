<template>
  <v-container
    fluid
    id="switch-component"
  >
    <div style="justify-content: center; display: flex;">
      <v-switch
        v-model="value"
        :label="`${value}`"
        false-value="Sync"
        true-value="Desync"
        hide-details
        color="#013b4d"
        :disabled="disabled"
      ></v-switch>
    </div>
  </v-container>
</template>

<style>

#switch-component {
  color-scheme: light dark;
}

#switch-component .v-selection-control__input:hover,
#switch-component .v-selection-control__input:focus {
  background-color: light-dark(#FF9D42, #A75000);
  color: light-dark(#FF9D42, #A75000);
}

</style>