<template>
  <v-window v-model="activeWindow" class="entity-window" show-arrows> 
    <v-window-item
      transition="fade-transition"
      reverse-transition="fade-transition"
      v-for="item in items" 
      :key="item.qid"
      :value="item.qid"
    >
      <entity-infobox class="entity-infobox" :qid="item.qid"></entity-infobox>
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
    }),
    watch: {
      selected: {
        handler: function () {
          console.log('EntityViewer.selected', this.selected)
          if (this.items.find(item => item.id === this.selected)) {
            // this.activeWindow = this.selected
          }        
        },
        immediate: true
      }
    }
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

