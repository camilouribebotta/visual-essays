<template>
  <v-container style="padding:0;">
    <v-row>
      <v-col>
        <essay/>
      </v-col>
      <v-col>
        <!-- <visualizer/> -->
        <!--
        <div class="text-center" style="position:fixed; top:0;">
          Visualizer
        </div>
        -->
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Essay from '../components/Essay'
import Visualizer from '../components/Visualizer'
export default {
  name: 'vertical-layout',
  components: {
    Essay,
    Visualizer
  }
}
</script>
