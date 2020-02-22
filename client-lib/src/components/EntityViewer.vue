<template>
  <v-window
    ref="entities"
    v-model="activeWindow"
    class="entity-window"
    showArrows
  > 
    <v-window-item
      transition="fade-transition"
      reverse-transition="fade-transition"
      v-for="item in items" 
      :key="item.qid"
      :value="item.qid"
    >
      <entity-infobox class="entity-infobox" :qid="item.qid"/>
    </v-window-item>
  </v-window>
</template>

<script>

  export default {
    name: 'EntityViewer',
    props: {
      items: { type: Array, default: () => ([]) }
    },
    data: () => ({
      activeWindow: undefined
    }),
    watch: {
      selectedItemID(selectedItemID) {
        if (this.items.find(item => item.id === selectedItemID)) {
          this.activeWindow = selectedItemID
        }
      }
    }
  }
</script>

<style>

  .entity-window {
    padding-top: 12px;
  }

  .entity-infobox {
    width: 600px;
    margin: auto;
    height: 100%;
    min-height: 165px;
  }

</style>

