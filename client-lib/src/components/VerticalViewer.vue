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
        @click.stop=""
        :href="`#${tab}`">
        <i :class="groups[tab].icon" class="fal"></i>
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
          :selected="activeTab"
          :width="viewerWidth"
          :height="viewerHeight"
          :initial-mode="mode"
          :hoverItemID="hoverItemID"
          :selectedItemID="selectedItemID"
          @hover-id="setHoverItemID"
          @selected-id="setSelectedItemID"
        />
      </v-tab-item>

    </v-tabs>

  </v-card>
</template>

<script>
  import { elemIdPath, itemsInElements, throttle } from '../utils'
  const tabOrder = ['imageViewer', 'mapViewer', 'videoViewer']

  export default {
    name: 'Viewer',
    data: () => ({
      paragraphs: {},
      spacer: undefined,
      tabs: [],
      activeTab: undefined,
      hoverElemId: undefined,
      viewerWidth: 0,
      header: undefined,
      contentContainer: 0,
      position: 'relative'
    }),
    computed: {
      viewportHeight() { return this.$store.getters.height },
      viewportWidth() { return this.$store.getters.width },
      headerSize() { return this.$store.getters.headerSize },
      headerHeight() { return this.$store.getters.headerHeight },
      footerHeight() { return this.$store.getters.footerHeight },
      viewerHeight() { return this.$store.getters.height - this.headerHeight - this.footerHeight},
      primary() {return this.$store.getters.itemsInActiveElements.find(item => item.primary === 'true' || item.tag === 'primary') },
      primaryTab() {
        let primary = this.primary ? `${this.primary.tag}` : undefined
        if (primary === 'map' || primary === 'image') {
          primary = `${primary}Viewer`
        }
        return primary
      },
      mode() { return this.primary ? this.primary.mode : undefined },
      hoverItemID() { return this.$store.getters.hoverItemID },
      selectedItemID() { return this.$store.getters.selectedItemID },
      style() {
        return {
          display: this.$refs.viewer ? 'block' : 'none',
          width: `${this.viewerWidth}px`,
          height: `${this.viewerHeight}px`
        }
      }
    },
    mounted() {
      console.log('VerticalViewer.mounted')
      // this.contentContainer = document.getElementById('scrollableContent')
      // this.header = document.getElementById('header')
      // this.contentContainer.addEventListener('scroll', throttle(this.mouseMove, 10))
      /*if (this.header && this.contentContainer) {
        this.contentContainer.addEventListener('scroll', throttle(this.mouseMove, 10))
        this.$store.dispatch('setContentStartPos', this.header.offsetHeight)
      } else {
        this.$refs.viewer.$el.style.top = '0px'
        this.$refs.viewer.$el.style.position = 'fixed'
        this.position = 'fixed'
      }*/
      this.viewerWidth = this.$refs.viewer.$el.parentElement.offsetWidth
      this.$nextTick(() => this.init())
    },
    methods: {
      setHoverItemID(itemID) {
        this.$store.dispatch('setHoverItemID', itemID)
      },
      setSelectedItemID(itemID) {
        this.$store.dispatch('setSelectedItemID', itemID)
      },
      /*
      (e) {
        if (!this.header) {
          this.header = document.getElementById('header')
        }
        if (this.header && this.$refs.viewer) {
          // console.log(this.header.clientHeight, this.headerSize)
          if (this.header.clientHeight === this.headerSize && this.position === 'relative') {
            this.$refs.viewer.$el.style.top = `${this.headerSize}px`
            this.$refs.viewer.$el.style.position = 'fixed'
            this.position = 'fixed'
            // console.log(`position=${this.position} ${this.header.offsetHeight}`)
          } else if (this.position === 'fixed' && this.header.offsetHeight > this.headerSize) {
            this.$refs.viewer.$el.style.top = '0px'
            this.$refs.viewer.$el.style.position = 'relative'
            this.position = 'relative'
          }
        }
        if (this.header.offsetHeight !== this.$store.getters.headerOffset) {
          this.$store.dispatch('setContentStartPos', this.header.offsetHeight)
        }
        // console.log(`position=${this.position} ${this.header.offsetHeight}`)
      },
      */
      init() {
        /*
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
                document.getElementById(paraId).scrollIntoView({block:'center'})
              }
            })
          }
          para.addEventListener('mouseenter', (e) => {
            const elemId = e.toElement.id
            console.log('mouseenter', elemId)
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
        */
        /*
        if (this.activeElement && this.paragraphs[this.activeElement]) {
          document.getElementById(this.activeElement).classList.add('active-elem')
          this.addItemClickHandlers(this.activeElement)
          const tabsBarElem = document.querySelector('.v-tabs-bar')
          if (tabsBarElem) {
            tabsBarElem.style.top = `${this.paragraphs[this.activeElement].top}px`
          }
        }
        this.addSpacer()
        */
      },
      addSpacer() {
        // Adds a spacer element that expands and contracts to match the size of the visualizer so
        // that content at the end of the article is still reachable by scrolling
        this.spacer = document.createElement('div')
        this.spacer.id = 'essay-spacer'
        this.spacer.style.height = `${this.viewportHeight*.8}px`
        document.getElementById('essay').appendChild(this.spacer)
      }
    },
    watch: {
      headerHeight: {
        handler: function () {
          // console.log('verticalViewer.watch.headerHeight', this.headerHeight)
          if (!this.header) {
            this.header = document.getElementById('header')
          }
          if (this.header && this.$refs.viewer) {
            // console.log(this.header.clientHeight, this.headerSize)
            if (this.header.clientHeight === this.headerSize && this.position === 'relative') {
              this.$refs.viewer.$el.style.top = `${this.headerSize}px`
              this.$refs.viewer.$el.style.position = 'fixed'
              this.position = 'fixed'
              // console.log(`position=${this.position} ${this.header.offsetHeight}`)
            } else if (this.position === 'fixed' && this.header.offsetHeight > this.headerSize) {
              this.$refs.viewer.$el.style.top = '0px'
              this.$refs.viewer.$el.style.position = 'relative'
              this.position = 'relative'
            }
          }
          //if (this.header.offsetHeight !== this.$store.getters.headerOffset) {
          //  this.$store.dispatch('setContentStartPos', this.header.offsetHeight)
          //}
        },
        immediate: true
      },
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
        // this.activeTab = (this.tabs.indexOf(this.activeTab) >= 0 ? this.activeTab : undefined) || this.primaryTab || availableGroups[0] 
        this.activeTab = this.primaryTab || availableGroups[0] 
        console.log(`availableGroups=${availableGroups} activeTab=${this.activeTab}`)
      },
      primary: {
        handler: function (value, prior) {
          console.log('primary', this.primary)
        },
        immediate: true
      },
      primaryTab: {
        handler: function (value, prior) {
          console.log(`primaryTab=${this.primaryTab}`)
          this.activeTab = this.primaryTab
        },
        immediate: true
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
      /*
      activeElement(active, prior) {
        if (prior) {
          // this.removeItemClickHandlers(prior)
          document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
        }
        // this.activeTab = undefined
        if (active && this.paragraphs[active]) {
          document.getElementById(active).classList.add('active-elem')
          // this.addItemClickHandlers(active)
          const tabsBarElem = document.querySelector('.v-tabs-bar')
          if (tabsBarElem) {
            tabsBarElem.style.top = `${this.paragraphs[active].top}px`
          }
        }
      }
    */
    }
  }
</script>

<style>

  #essay.vertical {
    background-color: #eaeaea;
    padding: 12px 0;
  }

  #essay.vertical .v-tabs-bar {
    border-radius: 0px;
    position: absolute;
    top: 43px;
    right: -20px;
    z-index: 2;
    height: unset;
    background-color :white !important;
  }
  
  #essay.vertical .v-tabs-bar .v-tabs-bar__content {
    flex-direction: column;
  }

  #essay.vertical .v-tabs-slider-wrapper {
    width: 0 !important;
  }

</style>

<style scoped>

  #viewer {
    background-color: #f5f5f5;
    height: 100vh;
    box-shadow: none;
    border-radius: 0;
    position: relative;
    top: 0px;
  }

  .v-tab {
    color: black !important;
    padding: 6px !important;
    min-width: 30px;
    max-width: 30px;
    font-size: 1.1em
   }

  .v-slide-group__wrapper {
    border-radius: 0px;
  }

  .v-tab--active {
    color: white !important;
    background-color: #1D5BC2 !important;
  }

</style>

