<template>
  <v-app id="visual-essay" :class="path">
    <component v-bind:is="layout"></component>
    <entity-infobox-dialog/>
  </v-app>
</template>

<script>
import HorizontalLayout from './layouts/HorizontalLayout'
import VerticalLayout from './layouts/VerticalLayout'

const breakpoint = 1000;

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
    layout: undefined
  }),
  computed: {
    viewportWidth() { return this.$store.getters.width }
  },
  watch: {
    viewportWidth: {
      handler: function (width) {
        console.log(this.$store.getters.layout)
        if (width > 0) {
          this.layout = this.$store.getters.layout || (width >= breakpoint ? 'vertical' : 'horizontal')
          console.log(`App.watch.viewportWidth: breakpoint=${breakpoint} width=${width} layout=${this.layout}`)
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

</style>
