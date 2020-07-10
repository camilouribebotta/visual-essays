<template>
  <v-card ref="viewer" id="viewer" :style="style">
    <v-tabs v-if="visualizerIsOpen"
      ref="tabs"
      v-model="activeTab"
      center-active
      show-arrows
      right
    >

      <v-tab 
        v-for="tab in tabs" :key="`tab-${tab}`"
        :href="`#${tab}`">
        <i :class="groups[tab].icon" class="fal" style="font-size:2.0rem;"></i>
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
          :width="viewerWidth"
          :height="viewerHeight"
        />
      </v-tab-item>

    </v-tabs>

    <span @click="closeViewer" style="position:absolute; top:6px; left:9px; cursor:pointer; z-index:2000;">
      <i class="fal fa-times" style="font-size:2.2rem; color:#1D5BC2; background:white; padding:3px 0 0 3px;"></i>
    </span>
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
      visualizerIsOpen: false,
      hoverElemId: undefined,
      selected: undefined,
      viewerWidth: 0
    }),
    computed: {
      viewportHeight() { return this.$store.getters.height },
      headerHeight() { return this.$store.getters.headerHeight },
      footerHeight() { return this.$store.getters.footerHeight },
      viewerHeight() { return this.viewportHeight/2 - 48 },
      viewportWidth() { return this.$store.getters.width },
      style() {
        return {
          display: this.$refs.viewer && this.visualizerIsOpen ? 'block' : 'none',
          position: 'fixed',
          top: `${this.viewportHeight/2}px`,
          height: `${this.viewerHeight}px`,
          width: `${this.viewerWidth}px`
        }
      }
    },
    mounted() {
      this.$store.dispatch('setTriggerOffset', 100)
      if (this.$store.getters.layout === 'ho') {
          this.visualizerIsOpen = true
      }
      this.viewerWidth = this.$refs.viewer.$el.parentElement.offsetWidth
      this.$nextTick(() => this.init())
    },
    methods: {
      init() {
        Array.from(document.body.querySelectorAll('p')).filter(elem => elem.id).forEach((para) => {
          para.title = elemIdPath(para.id).join(',')
          const itemsInPara = itemsInElements(elemIdPath(para.id), this.allItems)
          this.paragraphs[para.id] = {
            top: para.offsetTop,
            items: itemsInPara
          }
          if (itemsInPara.length > 0) {
            para.classList.add('has-items')
            para.addEventListener('click', (e) => {
              this.visualizerIsOpen = true
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
                // const scrollTo = this.paragraphs[paraId].top - offset
                // scrollable.scrollTo(0, scrollTo, )
              }
            })
          }
        })
        this.addSpacer()
      },
      addSpacer() {
        // Adds a spacer element that expands and contracts to match the size of the visualizer so
        // that content at the end of the article is still reachable by scrolling
        this.spacer = document.createElement('div')
        this.spacer.id = 'essay-spacer'
        this.spacer.style.height = 0
        document.getElementById('essay').appendChild(this.spacer)
      },
      openViewer(elemId) {
        if (this.paragraphs[elemId]) {
          this.visualizerIsOpen = true
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
        e.stopPropagation()
        const elemId = e.target.attributes['data-eid'].value
        this.$store.dispatch('setSelectedItemID', elemId)
      }
    },
    watch: {
      groups() {
        console.log(this.activeElement, this.groups)
        const availableGroups = []
        tabOrder.forEach(group => { if (this.groups[group]) availableGroups.push(group) })
        Object.keys(this.groups).forEach(group => {
          if (availableGroups.indexOf(group) === -1 && this.groups[group].icon) {
            availableGroups.push(group)
          }
        })
        this.tabs = availableGroups
        this.activeTab = (this.tabs.indexOf(this.activeTab) >= 0 ? this.activeTab : undefined) || this.primaryTab || availableGroups[0] 
        console.log(`availableGroups=${availableGroups} activeTab=${this.activeTab}`)
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
          if (this.visualizerIsOpen) {
            document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
          }
        }
        if (active) {
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

<style>

  #essay.horizontal {
    background-color: white;
  }

</style>

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

