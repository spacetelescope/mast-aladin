<template>
  <v-container
    fluid
    style="width: 100%; padding: 20px;"
  >
    <v-row>
      <v-col>
        <jupyter-widget :widget="source_widget" />
        <jupyter-widget :widget="destination_widget" />
      </v-col>
    </v-row>
    <jupyter-widget :widget="aspects_widget" />
    <jupyter-widget :widget="sync_widget" />
  </v-container>
</template>
