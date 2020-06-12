<template>
  <v-app id="visual-essay" :class="path">

    <template v-if="showBanner && essayConfig && essayConfig.banner">
      <site-header :essay-config="essayConfig" :progress="progress" @header-height="setHeaderHeight"></site-header>
      <v-sheet id="scrollableContent" class="overflow-y-auto">
        <v-container :style="`margin-top:${essayTopMargin}px; height:${height}px;`">
          <v-row v-if="layout === 'vtl'" no-gutters>
            <v-col class="essay-pane vtl"><essay></essay></v-col>
            <v-col class="map-pane vtl"><vertical-viewer></vertical-viewer></v-col>
          </v-row>
          <v-row v-else no-gutters>
            <v-col>
              <essay/>
              <horizontal-viewer/>
            </v-col>
          </v-row>
        </v-container>
      </v-sheet>
    </template>

    <v-container v-else :style="`margin-top:${essayTopMargin}px; height:${height}px`">
      <v-row v-if="layout === 'vtl'" no-gutters>
        <v-col class="essay-pane vtl"><essay/></v-col>
        <v-col class="map-pane vtl"><vertical-viewer/></v-col>
      </v-row>
      <v-row v-else no-gutters>
        <v-col>
          <essay/>
          <horizontal-viewer/>
        </v-col>
      </v-row>
    </v-container>
    
    <image-viewer-modal/>

  </v-app>
</template>

<script>

export default {
  name: 'app',
  props: {
    path: { type: String }
  },
  data: () => ({
    layout: 'vtl',
    bannerHeight: undefined
  }),
  computed: {
    isMobile() { return this.$store.getters.isMobile },
    viewportWidth() { return this.$store.getters.width },
    height() { return this.$store.getters.height },
    essayConfig() { return this.$store.getters.essayConfig },
    showBanner() { return this.$store.getters.showBanner },
    essayTopMargin() { return this.showBanner ? this.bannerHeight: 0 },
    progress() { return this.$store.getters.progress }
  },
  mounted() {
    this.layout = this.$store.getters.layout | this.layout
    console.log('App.mounted', this.showBanner, this.essayConfig)
  },
  methods: {
    setHeaderHeight(headerHeight) {
        this.$store.dispatch('setHeaderHeight', headerHeight)
    },
    setFooterHeight(footerHeight) {
      this.$store.dispatch('setFooterHeight', footerHeight)
    }
  },
  updated() {
    if (!this.bannerHeight) {
      const header = document.getElementById('header')
      if (header) {
        this.$store.dispatch('setHeaderSize', parseInt(header.style.minHeight.slice(0, header.style.minHeight.length - 2)))
        this.bannerHeight = parseInt(header.style.height.slice(0, header.style.height.length - 2))
      }
    }
  },
  watch: {
    viewportWidth: {
      handler: function (width) {
        if (width > 0) {
          this.layout = this.isMobile ? 'hc' : this.$store.getters.layout || 'vtl'
        }     
      },
      immediate: true
    }
  }
}
</script>

<style scoped>

  [v-cloak] { display: none; }

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

  .map-pane {
    z-index: 10;
  }

  .essay-pane.vtl  {
    z-index: 100;
    box-shadow: 5px 5px 10px 0px rgba(0,0,0,0.16);
  }
</style>
