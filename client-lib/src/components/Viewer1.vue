<template>
  <v-card id="viewer">
    <v-tabs
     v-if="activeWindow"
      ref="tabs"
      v-model="activeTab"
      center-active
      show-arrows
    >
      <v-tab v-if="maps.length > 0" href="#tab-0">
        Map
      </v-tab>
      <v-tab 
        v-for="itemsByCat in itemsByCategory"
        :key="`tab-${itemsByCat.tab}`"
        :href="`#tab-${itemsByCat.tab}`"
      >
        {{itemsByCat.category}}
      </v-tab>
      <v-tab-item
        transition="fade-transition"
        reverse-transition="fade-transition"
        v-if="maps.length > 0"         
        value="tab-0"
      >
        <lmap/>
      </v-tab-item>
      <v-tab-item
        transition="fade-transition"
        reverse-transition="fade-transition"
        v-for="(itemsByCat, tab) in itemsByCategory"
        :key="`tab-item-${tab+1}`"
        :value="`tab-${tab+1}`"
      >
        <v-window
          ref="entities"
          v-model="activeWindow[`tab${tab+1}`]"
          class="entity-window"
          showArrows
        > 
          <v-window-item
            transition="fade-transition"
            reverse-transition="fade-transition"
            v-for="(item, window) in itemsByCat.items" 
            :key="`tab-${itemsByCat.tab}-${window}`"
            :value="`window-${tab+1}-${window}`"
          >
            <div>{{`tab-${activeElement.id}-${itemsByCat.tab}`}} {{`tab-${activeElement.id}-${itemsByCat.tab}-${window}`}}</div>
            <entity-infobox class="entity-infobox" :qid="item.qid"/>
          </v-window-item>
        </v-window>
      </v-tab-item>
    </v-tabs>
  </v-card>      
</template>

<script>
  import Vue from 'vue'
  import Map from './Map'
  import EntityInfobox from './EntityInfobox'

  const catLabels = {
    location: 'Places',
    person: 'People',
    'fictional_character': 'Fictional Characters',
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
      activeTab: 'tab-0',
      activeWindow: undefined,
      itemsMap: {}
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
        const results = []
        let tab = 0
        this.itemsMap = {}
        const activeWindow = {}
        Object.keys(byCat).sort().forEach((key) => {
          tab += 1
          let _window = 0
          activeWindow[`tab${tab}`] = `window-${tab}-0`
          byCat[key].forEach((item) => {
            this.itemsMap[item.qid] = { tab, window: _window++}
          })
          results.push(
            {category: key, tab, items: byCat[key]}
          )
        })
        this.activeWindow = activeWindow
        return results
      }
    },
    methods: {
      clickHandler(e) {
        const selectedItem = this.itemsMap[e.toElement.attributes['data-entity'].value]
        this.activeTab = `tab-${selectedItem.tab}`
        this.activeWindow[`tab${selectedItem.tab}`] = `window-${selectedItem.tab}-${selectedItem.window}`
      }
    },
    watch: {
      activeElement(current, prior) {
        this.itemsByCategory
        if (prior) {
          document.getElementById(prior.id).querySelectorAll('.entity.inferred').forEach((entity) => {
            entity.removeEventListener('click', this.clickHandler)
          })
        }
        if (current) {
            document.getElementById(current.id).querySelectorAll('.entity.inferred').forEach((entity) => {
              entity.addEventListener('click', this.clickHandler)
            })
          }
      }
    }
  }
</script>

<style>

  .entity-window {
    padding-top: 12px;
  }

  .v-tabs-bar {
    background-color: #eee !important;
    height: 35px !important;
    margin-bottom: 3px;
    border-top: 1px solid #ccc !important;
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

