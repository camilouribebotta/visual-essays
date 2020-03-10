<template>
  <v-card ref="viewer" id="viewer" :style="style">
    <v-tabs v-if="visualizerIsOpen"
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
        <component 
          v-bind:is="groups[tab].component" 
          :items="groups[tab].items" 
          :selected="selected"
          :max-width="viewerWidth"
          :max-height="viewportHeight/2"
        />
      </v-tab-item>

    </v-tabs>

    <v-icon
      size="30"
      style="color:#aaa;position:absolute;top:0;left:0;cursor:pointer;padding:3px 0 0 3px;"
      @click="closeViewer"
    >
      mdi-close
    </v-icon>
  </v-card>
</template>

<script>
  import { addActivator } from './Activator'
  import { elemIdPath, itemsInElements } from '../utils'
  const tabOrder = ['map', 'image', 'video', 'location', 'place', 'person', 'plant', 'building', 'written_work', 'fictional_character', 'entity']

  export default {
    name: 'Viewer',
    data: () => ({
      paragraphs: {},
      spacer: undefined,
      tabs: [],
      activeTab: undefined,
      visualizerIsOpen: false,
      hoverElemId: undefined,
      selected: undefined,
      viewerWidth: 0
    }),
    computed: {
      viewportHeight() { return this.$store.getters.height },
      viewportWidth() { return this.$store.getters.width },
      style() {
        return {
          display: this.$refs.viewer && this.visualizerIsOpen ? 'block' : 'none',
          position: 'fixed',
          top: `${this.viewportHeight/2}px`,
          height: `${this.viewportHeight/2}px`,
          width: `${this.viewerWidth}px`
        }
      }
    },
    mounted() {
      this.viewerWidth = this.$refs.viewer.$el.parentElement.offsetWidth
      // this.waitForEssay()
      this.$nextTick(() => this.init())
    },
    methods: {
      waitForEssay() {
        console.log(`waitForEssay: found=${document.getElementById('essay') !== undefined}`)
        if (document.getElementById('essay')) {
          this.init()
        } else {
          setTimeout(() => { this.waitForEssay() }, 1000)
        }
      },
      init() {
        Array.from(document.body.querySelectorAll('p')).filter(elem => elem.id).forEach((para) => {
          para.title = elemIdPath(para.id).join(',')
          this.paragraphs[para.id] = {
            top: para.offsetTop,
            items: itemsInElements(elemIdPath(para.id), this.allItems)
          }
          // Display/enable activator when cursor hovers over paragraph element
          para.addEventListener('mouseenter', (e) => {
            const elemId = e.toElement.id
            if (this.hoverElemId && this.hoverElemId !== elemId) {
              const prior = document.querySelector(`[data-id="${this.hoverElemId}"]`)
              if (prior) { prior.style.display = 'none' }
            }
            this.hoverElemId = undefined
            if (!this.visualizerIsOpen) {
              this.hoverElemId = elemId
              document.querySelector(`[data-id="${this.hoverElemId}"]`).style.display = 'inline-block'
            }
          })
          /*
          para.addEventListener('mouseleave', (e) => {
            const elemId = e.toElement.id
            if (this.hoverElemId) {
              const prior = document.querySelector(`[data-id="${this.hoverElemId}"]`)
              if (prior) { prior.style.display = 'none' }
            }
            this.hoverElemId = undefined
          })
          */
        })
        this.addSpacer()
        this.addActivators()
      },
      addSpacer() {
        // Adds a spacer element that expands and contracts to match the size of the visualizer so
        // that content at the end of the article is still reachable by scrolling
        this.spacer = document.createElement('div')
        this.spacer.id = 'essay-spacer'
        this.spacer.style.height = 0
        document.getElementById('essay').appendChild(this.spacer)
      },
      addActivators() {
        const essay = document.getElementById('essay')
        Array.from(document.body.querySelectorAll('p')).filter(elem => elem.id).forEach((para) => {
          const paraData = this.paragraphs[para.id]
          if (paraData.items.length > 0) {
            addActivator(essay, para.id, paraData.top, paraData.items.map(item => item.id).join(','), this.activatorClickHandler)
          }
        })
      },
      openViewer(elemId) {
        if (this.paragraphs[elemId]) {
          this.visualizerIsOpen = true
          document.querySelectorAll('.activator').forEach(activator => activator.style.display = 'none')
          let offset = 100
          let scrollable = document.getElementById('scrollableContent')
          if (scrollable) {
            offset = -80
          } else {
            scrollable = window
          }
          const scrollTo = this.paragraphs[elemId].top - offset
          // console.log(`scrollTo: elem=${elemId} top=${scrollTo}`)
          this.spacer.style.height = `${this.viewportHeight*0.7}px`
          scrollable.scrollTo(0, scrollTo )
        }
      },
      closeViewer() {
        this.visualizerIsOpen = false
      },
      activatorClickHandler(e) {
        const selectedParaId = e.target.parentElement.attributes['data-id'].value
        this.openViewer(selectedParaId)
      },
      addItemClickHandlers(elemId) {
        document.getElementById(elemId).querySelectorAll('.inferred, .tagged').forEach((entity) => {
          entity.addEventListener('click', this.itemClickHandler)
        })
      },
      removeItemClickHandlers(elemId) {
      const elem = document.getElementById(elemId)
        if (elem) {
          document.getElementById(elemId).querySelectorAll('.inferred, .tagged').forEach((entity) => {
            entity.removeEventListener('click', this.itemClickHandler)
          })
        }
      },
      itemClickHandler(e) {
        const selectedItemId = e.toElement.attributes['data-itemid'].value 
        let found = false
        for (let groupId in this.groups) {
          const item = this.groups[groupId].items.find(item => item.id === selectedItemId)
          if (item) {
            this.activeTab = item.category === 'location' && this.groups.map
              ? 'map'
              : groupId
            break
          }
        }
        this.selected = selectedItemId
        console.log(`itemClickHandler: selected=${this.selected} tab=${this.activeTab}`)
      }
    },
    watch: {
      groups() {
        const availableGroups = []
        tabOrder.forEach(group => { if (this.groups[group]) availableGroups.push(group) })
        this.tabs = availableGroups
        if (!this.activeTab || availableGroups.indexOf(this.activeTab) < 0) {
          this.activeTab = availableGroups.length > 0 ? availableGroups[0] : undefined
        }
      },
      viewportHeight() {
        if (this.spacer) {
          this.spacer.style.height = `${this.viewportHeight/2}px`
        }
      },      
      viewportWidth() {   
        document.querySelectorAll('.activator').forEach((activator) => {
          const paraId = activator.attributes['data-id'].value
          activator.style.top = `${this.paragraphs[paraId].top}px`
        })
      },
      activeElement(active, prior) {
        if (prior) {
          this.removeItemClickHandlers(prior)
          // document.querySelector(`[data-id="${prior}"]`).style.display = 'none'
          if (this.visualizerIsOpen) {
            document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
          }
        }
        if (active) {
          this.addItemClickHandlers(active)
          // document.querySelector(`[data-id="${active}"]`).style.display = 'inline-block'
          if (this.visualizerIsOpen) {
            document.getElementById(active).classList.add('active-elem')
          }
        }
      },
      visualizerIsOpen(isOpen) {
        if (this.$refs.viewer) {
          this.$refs.viewer.$el.style.display = isOpen ? 'block' : 'none'
        }
        if (!isOpen) {
          this.spacer.style.height = 0
          document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
        } else if (this.activeElement) {
          this.spacer.style.height = `${this.viewportHeight*0.7}px`
          document.getElementById(this.activeElement).classList.add('active-elem')
        }
      }
    }
  }
</script>

<style scoped>

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

  p.active-elem {
    border-left: 4px solid #8FBC8F;
  }

  p.active-elem .inferred, p.active-elem .tagged {
    border-bottom: 2px solid #8FBC8F;
    cursor: pointer;
  }

  span.activator {
    display: none;
  }

  span.activator i {
    color: green !important;
    opacity: 0.5;
  }

  span.activator i:hover {
    color: green;
    opacity: 1;
  }

</style>

