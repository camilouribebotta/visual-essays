<template>
  <v-container>
    <v-row no-gutters v-if="layout === 'vtr'">
      <v-col class="essay-pane vtr "><essay/></v-col>
      <v-col class="map-pane vtr"><vertical-viewer/></v-col>
    </v-row>
    <v-row no-gutters v-else>
      <v-col class="map-pane vtl"><vertical-viewer/></v-col>
      <v-col class="essay-pane vtl"><essay/></v-col>
    </v-row>
  </v-container>
</template>

<script>
import Essay from '../components/Essay'
export default {
  name: 'vertical-layout',
  components: {
    Essay
  },
  computed: {
    layout() { return this.$store.getters.layout }
  }
}
</script>

<style scoped>

  .map-pane {
    z-index: 10;
  }

  .essay-pane.vtr  {
    z-index: 100;
    box-shadow: -5px 0px 10px 0px rgba(0,0,0,0.16);
  }

  .essay-pane.vtl  {
    z-index: 100;
    box-shadow: 5px 5px 10px 0px rgba(0,0,0,0.16);
  }

</style>