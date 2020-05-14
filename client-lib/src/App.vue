<template>
  <v-app id="visual-essay" :class="path">

    <v-card 
      v-if="showBanner && banner"
      tile class="overflow-hidden"
    >
      
      <v-app-bar
        id="appbar"
        app dark prominent
        elevate-on-scroll shrink-on-scroll
        elevation="5"
        :src="banner"
        :height="bannerHeight"
        scroll-target="#scrollableContent"
        :scroll-threshold="scrollThreshold"
      >

        <essay-header v-if="essayConfig" :essay-config="essayConfig" :progress="progress"></essay-header>

      </v-app-bar>

      <v-sheet id="scrollableContent" ref="scrollableContent" class="overflow-y-auto">
        <v-container ref="contentContainer" :style="`margin-top: ${essayTopMargin}px; height:${height}px;border:1px solid black;`">
          <component v-bind:is="layout"></component>
        </v-container>
      </v-sheet>

    </v-card>

    <v-container v-else ref="contentContainer" :style="`margin-top: ${essayTopMargin}px; height:${height}px`">
      <component v-bind:is="layout"></component>
    </v-container>

    <entity-infobox-dialog/>
  </v-app>
</template>

<script>
import HorizontalLayout from './layouts/HorizontalLayout'
import VerticalLayout from './layouts/VerticalLayout'
import EssayHeader from './components/EssayHeader'

const breakpoint = 768

export default {
  name: 'app',
  props: {
    path: { type: String }
  },
  components: {
    'horizontal': HorizontalLayout,
    'hc': HorizontalLayout,
    'ho': HorizontalLayout,
    'vertical': VerticalLayout,
    'vtl': VerticalLayout,
    'vtr': VerticalLayout,
    EssayHeader
  },
  data: () => ({
    layout: 'vtl',
    bannerHeight: 400,
    scrollThreshold: 400,
    extended: false,
  }),
  computed: {
    viewportWidth() { return this.$store.getters.width },
    height() { return this.$store.getters.height },
    essayConfig() { return this.$store.getters.essayConfig },
    banner() { return this.essayConfig ? this.essayConfig.banner : undefined },
    showBanner() { return this.$store.getters.showBanner },
    essayTopMargin() { return this.showBanner ? this.bannerHeight: 0 },
    title() { return 'Title' },
    progress() { return this.$store.getters.progress }
  },
  created() {
    this.$store.dispatch('setHeaderSize', 104)
  },
  mounted() {
    document.getElementById('appbar').addEventListener('wheel', this.throttle(this.scrollContent, 20))
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
    scrollContent(e) {
      const wheelDelta = e.wheelDelta
      this.$refs.scrollableContent.$el.scrollTo(0, this.$refs.scrollableContent.$el.scrollTop - wheelDelta)
    }
  },
  watch: {
    viewportWidth: {
      handler: function (width) {
        console.log(`width=${width} layout=${this.$store.getters.layout}`)
        if (width > 0) {
          this.layout = width <= breakpoint ? 'hc' : this.$store.getters.layout || 'vtl'
        }     
      },
      immediate: true
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
    background-color: #fff;
    padding: 0;
    margin: 0;
  }

  .container {
    padding: 0 !important;
    margin: 0;
    max-width: none !important;
  }

  #author-name {
    font-size: 1.2rem;
    margin: 0;
  }

  pre {
    margin-left: 36px;
    margin-bottom: 12px;
  }

  .v-toolbar, .v-footer, .v-navigation-drawer {
    z-index: 200 !important;
  }

  .v-toolbar__extension {
    padding: 0 !important;
    /* height: 100px !important; */
    background: white;
    color: black;
  }

  .v-toolbar__content {
    position: relative;
  }

  .v-app-bar__nav-icon {
    z-index: 20;
    margin-left: -22px!important;
    margin-top: 8px;
  }

  .v-toolbar__title {
    background-color: rgba(0, 0, 0, .75);
    width: 120%;
    margin-left: -42px;
    margin-right: -20px;
    padding: 8px 36px!important;
    position: relative;
    top: 4px;
  }

  .v-toolbar__image .v-image, .v-toolbar__content, #appbar{
    min-height: 104px!important;
  }

  #prog {
  height: 7px;
    margin-left: -36px;
    width: calc(100% + 72px);
    margin-right: -36px;
    position: relative;
    top: 3px;
  }

  .v-application .v-progress-linear__background.primary, .v-application .v-progress-linear__determinate.primary {
    background-color: #71CB2B!important;
    border-color: #71CB2B!important;
  }

</style>
