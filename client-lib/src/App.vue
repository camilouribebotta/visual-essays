<template>
  <v-app id="visual-essay" :class="path">

    <v-card
      v-if="showBanner && banner"
      tile class="overflow-hidden"
    >
      <v-app-bar
        id="appbar"
        app
        dense
        :height="bannerHeight"
        elevation="5"
        elevate-on-scroll
        dark
        shrink-on-scroll
        :src="banner"

        :scroll-threshold="scrollThreshold"
      >
        <v-toolbar-title v-if="this.$store.getters.layout==='vtl'">

          <essay-summary></essay-summary>
          <!--<v-progress-linear value="percentScrolled"></v-progress-linear>-->
        </v-toolbar-title>
        <v-toolbar-title v-else>Take an interactive and guided tour through the cultural history of plants</v-toolbar-title>


        <v-spacer></v-spacer>

      </v-app-bar>
      <v-sheet
        id="scrollableContent"
        class="overflow-y-auto"
      >
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
import EssaySummary from './components/EssaySummary'

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
    EssaySummary
  },
  data: () => ({
    layout: undefined,
    bannerHeight: 300,
    scrollThreshold: 350,
    extended: false,
  }),
  computed: {
    viewportWidth() { return this.$store.getters.width },
    height() { return this.$store.getters.height },
    banner() { return (this.$store.getters.items.filter(item => item.type === 'essay') || [{}])[0].banner },
    showBanner() { return this.$store.getters.showBanner },
    essayTopMargin() { return this.showBanner ? this.bannerHeight: 0 }
  },
  created() {
    this.$store.dispatch('setHeaderSize', 56)
  },
  watch: {
    viewportWidth: {
      handler: function (width) {
        console.log(`width=${width} layout=${this.$store.getters.layout}`)
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

  .v-toolbar__extension {
    padding: 0 !important;
    /* height: 100px !important; */
    background: white;
    color: black;
  }

  .v-toolbar__title {
    background-color: rgba(20%, 20%, 20%, .6);
    width: 120%;
    margin-left: -43px;
    margin-right: -20px;
    padding: 8px 36px!important;
  }
</style>
