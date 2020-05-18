<template>
  <v-container :style="style">
    <test/>
  </v-container>
</template>

<script>
  const test = httpVueLoader('/components/nested/Test.vue')
  module.exports = {
    name: 'entity',
    components: {
      test
    },
    props: {
      items: { type: Array, default: () => ([]) },
      selected: { type: String },
      maxWidth: { type: Number, default: 800 },
      maxHeight: { type: Number, default: 800 },
      initialMode: { type: String }
    },
    data: () => ({}),
    computed: { 
      style() { return {
        height: `${this.maxHeight}px`,
        width: `${this.maxWidth}px`,
        border: '1px solid red',
        padding: '6px'
      }}
    },
    mounted() {
      console.log('Entity component')
      console.log(this)
    }
  }
</script>

<style>
  
  [v-cloak] { display: none; }

</style>