<template>
  <v-container ref="container" style="padding:0;">
    <v-row no-gutters>
      <v-col>
        <essay/>
        <visualizer 
          id="visualizer"
          :style="`top:${visualizer.top}px; width:${visualizer.width}px;display:none`"
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
    Visualizer,
    Essay
  },
  data: () => ({
    visualizer: {}
  }),
  computed: {
    viewportHeight() { return this.$store.getters.height },
    viewportWidth() { return this.$store.getters.width }
  },
  mounted() {
    this.updateVisualizerPosition()
  },
  methods: {
    updateVisualizerPosition() {
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
