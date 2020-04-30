<template>
  <v-container class="summary">
    <v-row style="height:100%;" no-gutters>
      <v-col cols="12" sm="12">
          Essay title and summary/metadata
      </v-col>
    </v-row>
  </v-container>
</template>

<script>

  export default {
    name: 'EssaySummary',
    data: () => ({
    })
  }
</script>

<style>
  .summary {
    font-size: 14pt !important;
    height: 100%;
  }
</style>