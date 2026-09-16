<template>
  <div style="justify-content: center; display: flex;">
    <v-switch
      v-model="value"
      :label="`${value}`"
      false-value="Sync"
      true-value="Desync"
      hide-details
      color="success"
      inset
      :disabled="disabled"
    ></v-switch>
  </div>
</template>