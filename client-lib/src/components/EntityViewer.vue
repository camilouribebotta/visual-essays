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
      items: { type: Array, default: () => ([]) },
      selected: { type: String }
    },
    data: () => ({
      activeWindow: undefined
    }),
    mounted() {
      console.log(`${this.$options.name} mounted`)
    },
    watch: {
      selected: {
        handler: function () {
          if (this.items.find(item => item.id === this.selected)) {
            this.activeWindow = this.selected
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

