<template>
  <v-card ref="viewer" id="viewer" :style="style" >

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
          :max-height="viewportHeight"
        />
      </v-tab-item>

    </v-tabs>

  </v-card>
</template>

<script>
  import { elemIdPath, itemsInElements } from '../utils'
  const tabOrder = ['map', 'image', 'video']

  export default {
    name: 'Viewer',
    data: () => ({
      paragraphs: {},
      spacer: undefined,
      tabs: [],
      activeTab: undefined,
      visualizerIsOpen: true,
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
          width: `${this.viewerWidth}px`
        }
      }
    },
    mounted() {
      this.viewerWidth = this.$refs.viewer.$el.parentElement.offsetWidth
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
          para.addEventListener('click', (e) => {
            const paraId = e.target.tagName === 'P'
              ? e.target.id
              : e.target.parentElement.id
            if (this.paragraphs[paraId]) {
              let offset = 100
              let scrollable = document.getElementById('scrollableContent')
              if (scrollable) {
                offset = -80
              } else {
                scrollable = window
              }
              const scrollTo = this.paragraphs[paraId].top - offset
              scrollable.scrollTo(0, scrollTo, )
            }
          })
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
        })
        this.addSpacer()
      },
      addSpacer() {
        // Adds a spacer element that expands and contracts to match the size of the visualizer so
        // that content at the end of the article is still reachable by scrolling
        this.spacer = document.createElement('div')
        this.spacer.id = 'essay-spacer'
        this.spacer.style.height = `${this.viewportHeight/2}px`
        document.getElementById('essay').appendChild(this.spacer)
      },
      addItemClickHandlers(elemId) {
        document.getElementById(elemId).querySelectorAll('.active-elem .inferred, .active-elem .tagged').forEach((entity) => {
          entity.addEventListener('click', this.itemClickHandler)
        })
      },
      removeItemClickHandlers(elemId) {
        const elem = document.getElementById(elemId)
        if (elem) {
          document.getElementById(elemId).querySelectorAll('.active-elem .inferred, .active-elem .tagged').forEach((entity) => {
            entity.removeEventListener('click', this.itemClickHandler)
          })
        }
      },
      itemClickHandler(e) {
        const elemId = e.target.attributes['data-itemid'].value
        this.$store.dispatch('setSelectedItemID', elemId)
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
        this.viewerWidth = this.$refs.viewer.$el.parentElement.offsetWidth
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
          // document.querySelector(`[data-id="${active}"]`).style.display = 'inline-block'
          if (this.visualizerIsOpen) {
            document.getElementById(active).classList.add('active-elem')
          }
          this.addItemClickHandlers(active)
        }
      },
      visualizerIsOpen(isOpen) {
        if (this.$refs.viewer) {
          this.$refs.viewer.$el.style.display = isOpen ? 'block' : 'none'
        }
        if (!isOpen) {
          document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
        } else if (this.activeElement) {
          document.getElementById(this.activeElement).classList.add('active-elem')
        }
      }
    }
  }
</script>

<style>

  path {
    stroke-width: 2px;
  }

  #viewer {
    background-color: #000000;
    position: fixed;
    height: 100vh;
    box-shadow: none;
    border-radius: 0;
  }

  .v-tabs-bar {
    border-radius: 4px;
    position: absolute;
    top: 16px;
    right: 16px;
    z-index: 2;
    background-color :white !important;
    height: 36px !important;
  }

  .v-tab {
    color: black !important;
    padding: 0 6px !important;
  }

  .v-slide-group__wrapper {
    height: 36px;
    border-radius: 4px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.65);
  }

  .v-tab--active {
    color: white !important;
    padding: 0 6px !important;
    background-color :#1D5BC2 !important;
  }

</style>

