<template>
  <div
    class="text-center"
    style="height:100%;"
  >
    <viewer/>
  </div>
</template>

<script>
import Viewer from './Viewer'

export default {
  name: 'visualizer',
  components: {
    Viewer
  },
  computed: {
    height() { return this.$store.getters.height}
  },
}
</script>

<style>

  #viewer {
    height: 100%;
    margin-top: 3px;
  }

  .v-tabs-bar {
    background-color: #eee !important;
    height: 35px !important;
    margin-bottom: 3px;
    border-top: 1px solid #ccc !important;
  }

</style>
