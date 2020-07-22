<template>
  <v-card ref="viewer" id="viewer" :style="style" >
    <template v-if="layout === 'vtl'">
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
    </template>

    <template v-else>
      <v-tabs v-if="viewerIsOpen"
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
            :width="viewerWidth"
            :height="viewerHeight"
          />
        </v-tab-item>

      </v-tabs>

      <span @click="closeViewer" style="position:absolute; top:6px; left:9px; cursor:pointer; z-index:2000;">
        <i class="fal fa-times" style="font-size:2.2rem; color:#1D5BC2; background:white; padding:3px 0 0 3px;"></i>
      </span>

    </template>

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
      layout() { return this.$store.getters.layout },
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
      selectedParagraphID() { return this.$store.getters.selectedParagraphID },
      viewerIsOpen() { return this.$store.getters.viewerIsOpen },
      style() {
        if (this.layout === 'vtl') {
          return {
            display: this.$refs.viewer ? 'block' : 'none',
            width: `${this.viewerWidth}px`,
            height: `${this.viewerHeight}px`
          }
        } else {
          return {
            display: this.$refs.viewer && this.viewerIsOpen ? 'block' : 'none',
            position: 'fixed',
            top: `${this.viewportHeight/2}px`,
            height: `${this.viewerHeight}px`,
            width: `${this.viewerWidth}px`
          }
        }
      }
    },
    mounted() {
      this.$store.dispatch('setViewerIsOpen', this.layout === 'vtl' || this.layout === 'ho')
      console.log(`Viewer.mounted: viewerIsOpen=${this.viewerIsOpen}`)
      this.viewerWidth = this.$refs.viewer.$el.parentElement.offsetWidth
      this.$nextTick(() => this.init())
    },
    methods: {
      init() {
        this.addSpacer()
      },
      closeViewer() {
        this.$store.dispatch('setViewerIsOpen', false)
      },
      setHoverItemID(itemID) {
        console.log(`setHoverItemID=${itemID}`)
        this.$store.dispatch('setHoverItemID', itemID)
      },
      setSelectedItemID(itemID) {
        this.$store.dispatch('setSelectedItemID', itemID)
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
        },
        immediate: true
      },
      groups() {
        // console.log(this.activeElement, this.groups)
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
        // console.log(`availableGroups=${availableGroups} activeTab=${this.activeTab}`)
      },
      primaryTab: {
        handler: function (value, prior) {
          // console.log(`primaryTab=${this.primaryTab}`)
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
          this.viewerWidth = this.$refs.viewer.$el.parentElement.offsetWidth
        },
        immediate: false
      },
      viewerIsOpen: {
        handler: function (isOpen) {
          if (this.layout !== 'vtl') {
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
        },
        immediate: false
      },
      selectedParagraphID: {
        handler: function () {
          if (this.selectedParagraphID) {
            this.$store.dispatch('setViewerIsOpen', true)
            this.$store.dispatch('setSelectedParagraphID')
          }
        },
        immediate: false
      }
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

