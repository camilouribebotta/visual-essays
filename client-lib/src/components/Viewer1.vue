<template>
  <v-card id="viewer">
  
    <v-tabs vertical>
      <v-tab v-if="maps.length > 0" href="#tab-item-0">Map</v-tab>
      <v-tab 
        v-for="(itemsByCat, i) in itemsByCategory"
        :key="`tab-${i+1}`"
        :href="`#tab-item-${i+1}`"
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
        :key="`tab-item-${i+1}`"
        :value="`tab-item-${i+1}`"
      >
        <v-tabs vertical>
          <v-tab 
            v-for="(item, j) in itemsByCat.items"
            :key="`tab-${i}-${j+1}`"
            :href="`#tab-item-${i}-${j+1}`"
          >
            {{item.label}}
          </v-tab>
          <v-tab-item
            transition="fade-transition"
            reverse-transition="fade-transition"
            v-for="(item, j) in itemsByCat.items"
            :key="`tab-item-${i}-${j+1}`"
            :value="`tab-item-${i}-${j+1}`"
          >
            <entity-infobox class="entity-infobox" :qid="item.qid"/>
          </v-tab-item>
        </v-tabs>
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
    data: () => ({}),
    computed: {
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

  #viewer {
    height: 100%;
  }

  .entity-infobox {
    width: 600px;
    height: 100%;
    margin-left: 60px;
    min-height: 165px;
  }

</style>

