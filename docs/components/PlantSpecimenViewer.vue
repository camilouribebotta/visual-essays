<template>
  <v-container :style="containerStyle">
    <pre v-for="item in items" :key="item.id">{{item}}</pre>
  </v-container>
</template>

<script>
  module.exports = {
    name: 'network',
    props: { items: Array, width: Number, height: Number },
    computed: {
      containerStyle() { return { width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important' } }
    }
  }
</script>
