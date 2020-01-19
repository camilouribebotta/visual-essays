<template>
  <v-card id="viewer">
    <v-tabs>
      <v-tab v-if="maps.length > 0" href="#tab-item-0">Map</v-tab>
      <v-tab 
        v-for="(itemsByCat, i) in itemsByCategory"
        :key="`tab-${activeElement.id}-${i+1}`"
        :href="`#tab-item-${activeElement.id}-${i+1}`"
      >
        {{itemsByCat.category}}
      </v-tab>
      <v-tab-item
        transition="fade-transition"
        reverse-transition="fade-transition"
        v-if="maps.length > 0" 
        value="tab-item-0"
      >
        <lmap/>
      </v-tab-item>
      <v-tab-item
        transition="fade-transition"
        reverse-transition="fade-transition"
        v-for="(itemsByCat, i) in itemsByCategory"
        :key="`tab-item-${activeElement.id}-${i+1}`"
        :value="`tab-item-${activeElement.id}-${i+1}`"
      >
        <v-window
          class="elevation-1"
          showArrows
        > 
          <v-window-item
            transition="fade-transition"
            reverse-transition="fade-transition"
            v-for="item in itemsByCat.items" 
            :key="`${activeElement}-${item.id}`"
          >
            <entity-infobox class="entity-infobox" :qid="item.qid"/>
          </v-window-item>
        </v-window>
      </v-tab-item>
    </v-tabs>
  </v-card>      
</template>

<script>
  import Map from './Map'
  import EntityInfobox from './EntityInfobox'

  const catLabels = {
    location: 'Places',
    plant: 'Plants',
    entity: 'Entities'
  }

  export default {
    name: 'Viewer',
    components: {
      lmap: Map,
      EntityInfobox
    },
    data: () => ({
      window: 0,
      windows: {},
    }),
    computed: {
      activeElement() { return this.$store.getters.activeElement },
      entities() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'entity') },
      title() { return this.$store.getters.activeElement ? this.$store.getters.activeElement.title ? this.$store.getters.activeElement.title : this.$store.getters.activeElement.id : null },
      maps() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'map') },
      itemsByCategory() {
        const byCat = {}
        this.entities.forEach((entity) => {
          const category = catLabels[entity.category] || entity.category || 'unspecified'
          if (!byCat[category]) {
            byCat[category] = []
          }
          byCat[category].push(entity)
        })
        Object.entries(byCat).forEach(val => console.log('cat', val[0], val[1].length))
        const results = []
        Object.keys(byCat).sort().forEach((key) => {
          results.push({category: key, items: byCat[key]})
        })
        return results
      }
    }
  }
</script>

<style>

  .v-tabs-bar__content {
    min-width: 150px;
  }

  #viewer {
    height: 100%;
  }

  .close-button {
    position: absolute;
    left: 0;
    top: 6px;
  }

  .entity-infobox {
    width: 600px;
    margin: auto;
    height: 100%;
    min-height: 165px;
  }

</style>

