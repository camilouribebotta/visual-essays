<template>
  <v-container style="padding:0;">
    <v-row>
      <v-col>
        <vertical-viewer/>
      </v-col>
      <v-col>
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
