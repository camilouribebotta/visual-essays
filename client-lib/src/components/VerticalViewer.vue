<template>
  <v-card ref="viewer" id="viewer" :style="style" >

    <v-tabs
      id="control-tabs"
      ref="tabs"
      v-model="activeTab"
      :vertical=true
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
      hoverElemId: undefined,
      selected: undefined,
      viewerWidth: 0,
      header: undefined,
      position: 'relative'
    }),
    computed: {
      viewportHeight() { return this.$store.getters.height },
      viewportWidth() { return this.$store.getters.width },
      primaryTab () {
        const primary = this.$store.getters.itemsInActiveElements.find(item => item.type === 'primary')
        return primary ? primary.primary : undefined
      },
      style() {
        return {
          display: this.$refs.viewer ? 'block' : 'none',
          width: `${this.viewerWidth}px`
        }
      }
    },
    mounted() {
      this.header = document.getElementById('appbar')
      if (this.header) {
        document.getElementById('scrollableContent').addEventListener('scroll', this.throttle(this.mouseMove, 10))
        this.$store.dispatch('setContentStartPos', this.header.offsetHeight)
      } else {
        this.$refs.viewer.$el.style.top = '0px'
        this.$refs.viewer.$el.style.position = 'fixed'
        this.position = 'fixed'
      }
      this.viewerWidth = this.$refs.viewer.$el.parentElement.offsetWidth
      this.$nextTick(() => this.init())
    },
    methods: {
      throttle(callback, interval) {
        let enableCall = true

        return function(...args) {
          if (!enableCall) return
          enableCall = false
          callback.apply(this, args)
          setTimeout(() => enableCall = true, interval)
        }
      },
      mouseMove(e) {
        if (this.header.clientHeight === 56 && this.position === 'relative') {
          this.$refs.viewer.$el.style.top = '56px'
          this.$refs.viewer.$el.style.position = 'fixed'
          this.position = 'fixed'
          // console.log(`position=${this.position} ${this.header.offsetHeight}`)
        } else if (this.position === 'fixed' && this.header.offsetHeight > 56) {
          this.$refs.viewer.$el.style.top = '0px'
          this.$refs.viewer.$el.style.position = 'relative'
          this.position = 'relative'
        }
        if (this.header.offsetHeight !== this.$store.getters.headerOffset) {
          this.$store.dispatch('setContentStartPos', this.header.offsetHeight)
        }
        // console.log(`position=${this.position} ${this.header.offsetHeight}`)
      },
      waitForEssay() {
        // console.log(`waitForEssay: found=${document.getElementById('essay') !== undefined}`)
        if (document.getElementById('essay')) {
          this.init()
        } else {
          setTimeout(() => { this.waitForEssay() }, 1000)
        }
      },
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
          }
          para.addEventListener('mouseenter', (e) => {
            const elemId = e.toElement.id
            if (this.hoverElemId && this.hoverElemId !== elemId) {
              const prior = document.querySelector(`[data-id="${this.hoverElemId}"]`)
              if (prior) { prior.style.display = 'none' }
            }
            this.hoverElemId = elemId
            const elem = document.querySelector(`[data-id="${this.hoverElemId}"]`)
            if (elem) {
              elem.style.display = 'inline-block'
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
        this.spacer.style.height = `${this.viewportHeight*.8}px`
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
        e.stopPropagation()
        const elemId = e.target.attributes['data-itemid'].value
        this.$store.dispatch('setSelectedItemID', elemId)
      }
    },
    watch: {
      groups() {
        const availableGroups = []
        tabOrder.forEach(group => { if (this.groups[group]) availableGroups.push(group) })
        this.tabs = availableGroups
        this.activeTab = this.primaryTab || availableGroups[0] 
      },
      viewportHeight: {
        handler: function (value, prior) {
          // console.log('viewportHeight', this.viewportHeight)
          if (this.spacer) {
            this.spacer.style.height = `${this.viewportHeight/2}px`
          }
        },
        immediate: true
      },
      viewportWidth: {
        handler: function (value, prior) {
          // console.log(this.$refs.viewer.$el)
          this.viewerWidth = this.$refs.viewer.$el.parentElement.offsetWidth
        },
        immediate: false
      },
      activeElement(active, prior) {
        if (prior) {
          this.removeItemClickHandlers(prior)
          document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
        }
        if (active) {
          document.getElementById(active).classList.add('active-elem')
          this.addItemClickHandlers(active)
        }
      }
    }
  }
</script>

<style>

  #viewer {
    background-color: #f5f5f5;
    /* position: relative; */
    height: 100vh;
    box-shadow: none;
    border-radius: 0;
  }

  .v-tabs-bar {
    border-radius: 4px;
    position: absolute;
    top: 44px;
    right: -42px;
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

