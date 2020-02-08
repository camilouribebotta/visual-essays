<template>
  <v-container ref="container" style="padding:0;">
    <v-row no-gutters>
      <v-col>
        <essay :style="`height:${essay.height}px;`"/>
        <visualizer 
          id="visualizer"
          :style="`top:${visualizer.top}px; width:${visualizer.width}px;display:${visualizerIsOpen ? 'block': 'none'}`"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Essay from '../components/Essay'
import Visualizer from '../components/Visualizer'
export default {
  name: 'horizontal-layout',
  components: {
    Essay,
    Visualizer
  },
  data: () => ({
    essay: {},
    visualizer: {}
  }),
  computed: {
    visualizerIsOpen() { return this.$store.getters.visualizerIsOpen },
    viewportHeight() { return this.$store.getters.height },
    viewportWidth() { return this.$store.getters.width }
  },
  methods: {
    updateVisualizerPosition() {
      this.essay = { height: this.visualizerIsOpen }
      this.visualizer = {
        top: this.viewportHeight/2,
        height: this.viewportHeight/2,
        width: this.$refs.container.offsetWidth
      }
    }
  },
  watch: {
    viewportHeight() { this.updateVisualizerPosition() },
    viewportWidth() { this.updateVisualizerPosition() }
  }
}
</script>

<style>

  #visualizer {
    position: fixed;
  }

</style>
