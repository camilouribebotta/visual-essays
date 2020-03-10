<template>
  <v-container>
    <v-row>
      <v-col>
        <vertical-viewer/>
      </v-col>
      <v-col class="essay-pane">
        <essay/>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Essay from '../components/Essay'
export default {
  name: 'vertical-layout',
  components: {
    Essay
  }
}
</script>

<style scoped>

  .col {
    margin: 3px;
    padding: 0;
  }
  .essay-pane {
    box-shadow: 0px 3px 1px -2px rgba(0, 0, 0, 0.2), 0px 2px 2px 0px rgba(0, 0, 0, 0.14), 0px 1px 5px 0px rgba(0, 0, 0, 0.12);
    /*
      -webkit-box-shadow: -1px 1px 2px 2px rgba(10,10,10,0.7); 
      box-shadow: -1px 1px 2px 2px rgba(10,10,10,0.7);  
    */
  }

</style>