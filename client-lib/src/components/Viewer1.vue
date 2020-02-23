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
      hoverElemId: undefined
    }),
    computed: {
      viewportHeight() { return this.$store.getters.height },
      viewportWidth() { return this.$store.getters.width },
    },
    mounted() {
      this.waitForEssay()
    },
    methods: {
      waitForEssay() {
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
          para.addEventListener('mouseenter', (e) => {
            const elemId = e.toElement.id
            console.log('mouseenter', elemId)
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
          para.addEventListener('mouseleave', (e) => {
            const elemId = e.toElement.id
            // console.log('mouseleave', elemId)
            if (this.hoverElemId) {
              const prior = document.querySelector(`[data-id="${this.hoverElemId}"]`)
              // if (prior) { prior.style.display = 'none' }
            }
            // this.hoverElemId = undefined
          })
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
        // console.log('addActivators')
        const essay = document.getElementById('essay')
        Array.from(document.body.querySelectorAll('p')).filter(elem => elem.id).forEach((para) => {
          const paraData = this.paragraphs[para.id]
          //console.log(`${para.id} items=${paraData.items.map(item => item.id).join(',')}`)
          if (paraData.items.length > 0) {
            addActivator(essay, para.id, paraData.top, paraData.items.map(item => item.id).join(','), this.clickHandler)
          }
        })
      },
      openViewer(elemId) {
        if (this.paragraphs[elemId]) {
          // this.$store.dispatch('setVisualizerIsOpen', true)
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
          console.log(this.viewportHeight, this.spacer)
          scrollable.scrollTo(0, scrollTo )
        }
      },
      closeViewer() {
        // this.$store.dispatch('setVisualizerIsOpen', false)
        this.visualizerIsOpen = false
        // document.querySelectorAll('.activator').forEach(activator => activator.style.display = 'block')
        // document.querySelector(`[data-id="${this.activeElement}"]`).style.display = 'inline-block'
      },
      clickHandler(e) {
        const selectedParaId = e.target.parentElement.attributes['data-id'].value
        this.openViewer(selectedParaId)
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
        }
      },
      visualizerIsOpen(isOpen) {
        document.getElementById('visualizer').style.display = isOpen ? 'block' : 'none'
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

  span.activator {
    display: none;
  }

  span.activator i {
    color: #eee;
    opacity: 0.4;
  }

  span.activator i:hover {
    color: blue;
    opacity: 1;
  }

</style>

