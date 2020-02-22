<template>
  <v-card id="viewer" v-if="visualizerIsOpen">
    <v-tabs
      ref="tabs"
      v-model="activeTab"
      center-active
      show-arrows
    >

      <v-tab 
        v-for="tab in tabs" :key="`tab-${tab}`"
        :href="`#${tab}`">
        {{groups[tab].label || tab}}
      </v-tab>

      <v-tab-item
        transition="fade-transition"
        reverse-transition="fade-transition"
        v-for="tab in tabs" :key="`tab-item-${tab}`"
        :value="tab"
      >    
        <component v-bind:is="groups[tab].component" :items="groups[tab].items"></component>
      </v-tab-item>

    </v-tabs>

    <v-icon
      size="30"
      style="color:#aaa;position:absolute;top:0;left:0;cursor:pointer;padding:3px 0 0 3px;"
      @click="close"
    >
      mdi-close
    </v-icon>
  </v-card>      
</template>

<script>
  const tabOrder = ['map', 'image', 'video', 'location', 'place', 'person', 'plant', 'building', 'written_work', 'fictional_character', 'entity']

  export default {
    name: 'Viewer',
    data: () => ({
      tabs: [],
      activeTab: undefined
    }),
    methods: {
      close() {
        this.$store.dispatch('setVisualizerIsOpen', false)
        document.querySelectorAll('.activator').forEach(activator => activator.style.display = 'block')
      }
    },
    watch: {
      groups() {
        const availableGroups = []
        tabOrder.forEach(group => { if (this.groups[group]) availableGroups.push(group) })
        this.tabs = availableGroups
        if (!this.activeTab) {
          this.activeTab = availableGroups.length > 0 ? availableGroups[0] : undefined
        }
      },
      selectedItemID() {
        let found = false
        if (this.selectedItemID) {
          for (let groupId in this.groups) {
            if (this.groups[groupId].items.find(item => item.id === this.selectedItemID)) {
              this.activeTab = groupId
              break
            }
          }
        }
      }
    }
  }
</script>

<style>

  #viewer {
    height: 100%;
  }

  .v-tabs-bar {
    background-color: #eee !important;
    height: 35px !important;
    margin-bottom: 3px;
    border-top: 1px solid #ccc !important;
  }

  .v-tabs-bar__content {
    margin-left: 24px;
  }

  .close-button {
    position: absolute;
    left: 0;
    top: 6px;
  }

</style>

