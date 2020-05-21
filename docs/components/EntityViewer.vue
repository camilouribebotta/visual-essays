<template>
  <v-window v-model="activeWindow" class="entity-window" show-arrows> 
    <v-window-item
      transition="fade-transition"
      reverse-transition="fade-transition"
      v-for="item in items" 
      :key="item.eid"
      :value="item.eid"
    >
      <entity-infobox class="entity-infobox" :eid="item.eid"></entity-infobox>
    </v-window-item>
  </v-window>
</template>

<script>

  module.exports = {
    name: 'EntityViewer',
    props: {
      items: { type: Array, default: () => ([]) },
      selected: { type: String }
    },
    data: () => ({
      activeWindow: undefined
    })
  }

</script>

<style>

  .entity-window {
    padding: 16px;
  }

  .entity-infobox {
    padding: 16px;
    margin: auto;
    height: 100%;
    min-height: 165px;
  }

</style>

