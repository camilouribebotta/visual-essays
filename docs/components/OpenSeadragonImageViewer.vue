<template>
  <div id="osd" :style="containerStyle"></div>
</template>
<script>

module.exports = {
  name: 'OpenSeadragonImageViewer',
  props: {
    items: Array,
    width: Number,
    height: Number
  },
  data: () => ({
    viewer: undefined
  }),
  computed: {
    containerStyle() { return { position: 'relative', width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important' } },
  },
  mounted() {
    console.log('OpenSeadragonImageViewer.mounted', this.items)
    this.init()
  },
  methods: {
    init() {
      if (this.viewer) {
        this.viewer.destroy()
      }
      this.viewer = OpenSeadragon({
        id: 'osd',
        tileSources: this.items[0].url + '/info.json',
        showNavigationControl: false,
        minZoomImageRatio: 0.2,
        maxZoomPixelRatio: 5
      })
    }
  },
  watch: {
    items: {
      handler: function (value, prior) {
        console.log('OpenSeadragonImageViewer.items', this.items)
        this.init()
      },
      immediate: false
    }
  }
}
</script>

<style>
</style>