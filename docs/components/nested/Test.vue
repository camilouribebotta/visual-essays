<template>
  <v-container>
    Nested Test
  </v-container>
</template>

<script>
  module.exports = {
    name: 'test',
    data: () => ({}),
    mounted() { console.log('Test component') }
  }
</script>

<style>
  
  [v-cloak] { display: none; }

</style>