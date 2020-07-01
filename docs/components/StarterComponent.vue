<template>
  <v-container :style="containerStyle">
    <pre v-for="item in items" :key="item.id">{{JSON.stringify(item, Set_toJSON, 2)}}</pre>
  </v-container>
</template>

<script>

module.exports = {
  name: 'starterComponent',
  props: { items: Array, width: Number, height: Number },
  data: () => ({}),
  computed: {
    containerStyle() { return { width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important' } },
  },
  mounted() {
    console.log(this.$options.name, this.items)
  },
  methods: {
    // Converts Set to array for JSON.stringify
    Set_toJSON(key, value) {
      if (typeof value === 'object' && value instanceof Set) {
        return [...value]
      }
      return value;
    }
  }
}
</script>

<style scoped>
  pre {
    margin-left: 20px;
  }
</style>
