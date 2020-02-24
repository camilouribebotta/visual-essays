<template>
  <v-app id="visual-essay">
    <component v-bind:is="layout"></component>
    <entity-infobox-dialog/>
  </v-app>
</template>

<script>
import HorizontalLayout from './layouts/HorizontalLayout'
import VerticalLayout from './layouts/VerticalLayout'

export default {
  name: 'app',
  components: {
    'horizontal': HorizontalLayout,
    'vertical': VerticalLayout
  },
  computed: {
    layout() { return this.$store.getters.layout }
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
    padding: 0;
    margin: 0;
    max-width: none;
  }
</style>
