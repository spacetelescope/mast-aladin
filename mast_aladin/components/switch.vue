<template>
  <v-container
    fluid
    id="switch-component"
  >
    <v-tooltip
      location="top"
      :open-delay="1000"
      content-class="tooltip"
    >
      <template #activator="{ props }">
        <span v-bind="props" class="sync-button-activator">
          <v-btn
            class="sync-action-btn"
            :disabled="disabled"
            :aria-label="disabled ? 'Synchronization unavailable' : `${value} synchronization`"
            rounded="0"
            variant="flat"
            @click="value = value === 'Sync' ? 'Desync' : 'Sync'"
          >
            {{ disabled ? 'Sync unavailable' : value }}
          </v-btn>
        </span>
      </template>
      {{ disabled
        ? 'Select a source and at least one destination to enable synchronization.'
        : `${value === 'Sync' ? 'Start' : 'Stop'} synchronizing the selected viewport properties.`
      }}
    </v-tooltip>
  </v-container>
</template>

<style>
#switch-component {
  display: flex;
}

#switch-component .sync-button-activator {
  display: flex;
  width: 100%;
}

#switch-component .sync-action-btn {
  width: 100%;
  background-color: #013b4d;
  color: white;
  font-weight: 900;
  letter-spacing: 1.25px;
}

#switch-component .sync-action-btn:hover,
#switch-component .sync-action-btn:focus-visible {
  background-color: light-dark(#FF9D42, #A75000);
}

#switch-component .sync-action-btn.v-btn--disabled {
  background-color: light-dark(#d7dde0, #34454c);
  color: light-dark(#5f686c, #aeb9bd);
  opacity: 1;
}

</style>