<template>
  <v-app id="visual-essay" :class="path">

    <v-card
      v-if="showBanner && banner"
      tile class="overflow-hidden"
    >
      <v-app-bar
        id="appbar"
        app
        prominent
        :height="bannerHeight"
        elevate-on-scroll
        fade-img-on-scroll
        dark
        shrink-on-scroll
        :src="banner"
        scroll-target="#scrollableContent"
        :scroll-threshold="scrollThreshold"
      >
        <v-toolbar-title>Visual essay</v-toolbar-title>
        <v-spacer></v-spacer>
      </v-app-bar>

      <v-sheet
        id="scrollableContent"
        class="overflow-y-auto"
      >
        <v-container ref="contentContainer" :style="`margin-top: ${essayTopMargin}px; height:${height}px`">
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
    'vtr': VerticalLayout
  },
  data: () => ({
    layout: undefined,
    bannerHeight: 600,
    scrollThreshold: 550
  }),
  computed: {
    viewportWidth() { return this.$store.getters.width },
    height() { return this.$store.getters.height },
    banner() { return (this.$store.getters.items.filter(item => item.type === 'essay') || [{}])[0].banner },
    showBanner() { return this.$store.getters.showBanner },
    essayTopMargin() { return this.showBanner ? this.bannerHeight: 0 }
  },
  watch: {
    viewportWidth: {
      handler: function (width) {
        // console.log(`layout=${this.$store.getters.layout}`)
        if (width > 0) {
          this.layout = this.$store.getters.layout || (width >= breakpoint ? 'vtl' : 'hc')
          // console.log(`App.watch.viewportWidth: breakpoint=${breakpoint} width=${width} layout=${this.layout}`)
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

  pre {
    margin-left: 36px;
    margin-bottom: 12px;
  }

  .v-toolbar, .v-footer, .v-navigation-drawer {
    z-index: 200 !important;
  }

</style>
