<template>
  <v-card id="viewer" v-if="visualizerIsOpen">
    <v-tabs
     v-if="activeWindow"
      ref="tabs"
      v-model="activeTab"
      center-active
      show-arrows
    >
      <v-tab v-if="includeMapViewer" href="#tab-0">
        Map
      </v-tab>
      <v-tab v-if="includeImageViewer" href="#tab-1">
        Image viewer
      </v-tab>
      <v-tab v-if="includeVideoPlayer" href="#tab-2">
        Video
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
        v-if="includeMapViewer"         
        value="tab-0"
      >
        <lmap/>
      </v-tab-item>
      <v-tab-item
        transition="fade-transition"
        reverse-transition="fade-transition"
        v-if="includeImageViewer"         
        value="tab-1"
      >
        <image-viewer/>
      </v-tab-item>
      <v-tab-item
        transition="fade-transition"
        reverse-transition="fade-transition"
        v-if="includeVideoPlayer"         
        value="tab-2"
      >
        <video-player :videoId="videos[0].id"/>
      </v-tab-item>
      <v-tab-item
        transition="fade-transition"
        reverse-transition="fade-transition"
        v-for="(itemsByCat, tab) in itemsByCategory"
        :key="`tab-item-${tab+3}`"
        :value="`tab-${tab+3}`"
      >
        <v-window
          ref="entities"
          v-model="activeWindow[`tab${tab+3}`]"
          class="entity-window"
          showArrows
        > 
          <v-window-item
            transition="fade-transition"
            reverse-transition="fade-transition"
            v-for="(item, window) in itemsByCat.items" 
            :key="`tab-${itemsByCat.tab}-${window}`"
            :value="`window-${tab+3}-${window}`"
          >
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
  import ImageViewer from './ImageViewer'
  import VideoPlayer from './VideoPlayer'
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
      ImageViewer,
      VideoPlayer,
      EntityInfobox
    },
    data: () => ({
      activeTab: 'tab-0',
      activeWindow: undefined,
      itemsMap: {}
    }),
    mounted() {
      if (this.activeElement) {
        this.itemsByCategory
      }
    },
    computed: {
      selectedItemID () { return this.$store.getters.selectedItemID },
      activeElement() { return this.$store.getters.activeElement },
      activeElements() { return this.$store.getters.activeElements },
      itemsInActiveElements() { return this.$store.getters.itemsInActiveElements },
      configs() { return this.itemsInActiveElements.filter(item => item.type === 'config') },
      entities() { return this.itemsInActiveElements.filter(item => item.type === 'entity') },
      geojson() { return this.itemsInActiveElements.filter(item => item.type === 'geojson') },
      videos() { return this.itemsInActiveElements.filter(item => item.type === 'video') },
      title() { return this.$store.getters.activeElement ? this.$store.getters.activeElement.title ? this.$store.getters.activeElement.title : this.$store.getters.activeElement.id : null },
      includeMapViewer() { return this.itemsInActiveElements.filter(item => item.type === 'map').length > 0 },
      includeImageViewer() { return this.itemsInActiveElements.filter(item => item.type === 'image-viewer').length > 0 },
      includeVideoPlayer() { return this.videos.length > 0 },
      visualizerIsOpen() { return this.$store.getters.visualizerIsOpen },
      itemsByCategory() {
        let activeTab = this.includeMapViewer ? 'tab-0' : this.includeImageViewer ? 'tab-1' : 'tab-2'
        this.configs.filter(c => c.tab).forEach(c => activeTab = c.tab)
        this.activeTab = activeTab

        const byCat = {}
        this.geojson
        //.filter(geojson => geojson.label)
        .forEach((geojson) => {
          const category = 'Places'
          if (!byCat[category]) {
            byCat[category] = []
          }
          byCat[category].push(geojson)
        })
        this.entities
        //.filter(entity => entity.label)
        .forEach((entity) => {
          const category = catLabels[entity.category] || entity.category || 'unspecified'
          if (!byCat[category]) {
            byCat[category] = []
          }
          byCat[category].push(entity)
        })
        const results = []
        let tab = 2
        this.itemsMap = {}
        const activeWindow = {}
        Object.keys(byCat).sort().forEach((key) => {
          tab += 1
          let _window = 0
          activeWindow[`tab${tab}`] = `window-${tab}-0`
          byCat[key].forEach((item) => {
            this.itemsMap[item.id] = { tab, window: _window++}
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
      isLocation(id) {
        return this.entities.filter(e => e.id === id && e.category === 'location').length > 0 || this.geojson.filter(e => e.id == id).length > 0
      },
      clickHandler(e) {
        event.preventDefault()
        event.stopPropagation()
        const selectedItemID = e.toElement.attributes['data-itemid'].value
        const selectedItem = this.itemsMap[selectedItemID]
        this.activeTab = this.includeMapViewer && this.isLocation(selectedItemID)
          ? 'tab-0'
          : `tab-${selectedItem.tab}`
        this.activeWindow[`tab${selectedItem.tab}`] = `window-${selectedItem.tab}-${selectedItem.window}`
        // console.log(`clickHandler: activeTab=${this.activeTab} activeWindow=`, this.activeWindow)
        this.$store.dispatch('setSelectedItemID', selectedItemID)
      },
      addClickHandlers(elemId) {
        // console.log(`addClickHandlers ${elemId}`)
        document.getElementById(elemId).querySelectorAll('.inferred, .tagged').forEach((entity) => {
          entity.addEventListener('click', this.clickHandler)
        })
      },
      removeClickHandlers(elemId) {
        // console.log(`removeClickHandlers ${elemId}`)
        const elem = document.getElementById(elemId)
        if (elem) {
          document.getElementById(elemId).querySelectorAll('.inferred, .tagged').forEach((entity) => {
            entity.removeEventListener('click', this.clickHandler)
          })
        }
      }
    },
    watch: {
      activeElement: {
        handler: function (current, prior) {
          // console.log(`Viewer.activeElement: current=${current} prior=${prior}`)
          this.itemsByCategory
          if (current) {
            if (prior) {
              this.removeClickHandlers(prior)
            }            
            this.addClickHandlers(current)
          }
        },
        immediate: false
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

