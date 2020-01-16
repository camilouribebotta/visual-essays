<template>
  <v-app>
    <entity-infobox/>
    <bottom-sheet :show="false"/>
  </v-app>
</template>

<script>
import Vue from 'vue'
import entityInfobox from './components/EntityInfoboxDialog'
import bottomSheet from './components/BottomSheet'
import { get_entity } from './api'

// Initialize with default components
const components = {
  entityInfobox,
  bottomSheet
}

// Override defaults with custom components
if (window.data && window.data.customComponents) {
  for (let componentId in window.data.customComponents) {
    if (components[componentId]) {
      components[componentId] = `url:${window.data.customComponents[componentId]}`
    }
  }
}

export default {
  name: 'app',
  components,
  data: () => ({}),
  mounted() {
    this.$nextTick(() => this.init())
  },
  methods: {
    init() {
      this.aggregateItemMappings()
      this.findContent()
      // attach click listeners to entities
      document.body.querySelectorAll('.entity.tagged').forEach((entity) => {
        entity.addEventListener('click', this.onEntityClick)
      })
    },
    onEntityClick(e) {
      e.stopPropagation()
      const qid = e.target.attributes['data-entity'].value
      this.$store.dispatch('setSelectedEntityQID', qid)
      const entity = this.$store.getters.items.find(item => item.qid === qid)
      if (entity && !entity['summary info']) {
        get_entity(qid)
          .then((entity) => {
            entity.id = qid
            this.$store.dispatch('updateItem', entity)
          })
      }
    },
    getParagraphs(elem) {
      const paragraphs = []
      if (elem) {
        Array.prototype.slice.call(elem.getElementsByTagName('p')).forEach((para) => {
          if (para.id) {
            para.title = `${para.id} (${para.offsetTop})`
            paragraphs.push({
              id: para.id,
              top: para.offsetTop,
              bottom: para.offsetTop + para.offsetHeight,
              items: this.itemsPartOf(para.id),
            })
          }
        })
      }
      return paragraphs
    },
    findContent() {
      const content = this.getParagraphs(document.getElementById('essay'))
      for (let i = 1; i < 9; i++) {
        document.body.querySelectorAll(`h${i}`).forEach((heading) => {
          const sectionElem = heading.parentElement
          const sectionId = sectionElem.attributes.id.value
          //sectionElem.title = `${sectionId} (${sectionElem.offsetTop})`
          const section = {
            id: sectionId,
            level: i,
            title: heading.innerHTML,
            top: sectionElem.offsetTop,
            bottom: sectionElem.offsetTop + sectionElem.offsetHeight,
            items: this.itemsPartOf(sectionId),
            paragraphs: this.getParagraphs(sectionElem)
          }
          content.push(section)
        })
      }
      console.log(content)
      this.$store.dispatch('setContent', content)
    },
    aggregateItemMappings() {
      this.$store.getters.items.forEach((item) => {
        item.part_of = new Set()
        if (item.tagged_in) {
          item.tagged_in.forEach((elemId) => { item.part_of.add(elemId) }) 
        }        
        if (item.found_in) {
          item.found_in.forEach((elemId) => { item.part_of.add(elemId) }) 
        }
      })
    },
    itemsPartOf(elemId) {
      const items = []
      this.$store.getters.items.forEach((item) => {
        if (item.part_of.has(elemId) || (item.type !== 'entity' && item.part_of.has('essay'))) {
          items.push(item)
        }
      })
      return items
    }
  }
}
</script>

<style>
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: left;
    color: #2c3e50;
  }
  .v-application--wrap {
    min-height: 0 !important;
  }
</style>
