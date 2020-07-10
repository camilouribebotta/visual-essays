<template>
  <div id="osd" :style="containerStyle"></div>
</template>
<script>

module.exports = {
  name: 'OpenSeadragonImageViewer',
  props: {
    items: Array,
    width: Number,
    height: Number,
    defaultFit: {type: String, default: 'cover'}
  },
  data: () => ({
    viewer: undefined,
    center: undefined,
    zoom: undefined
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
      const item = this.items[0]
      this.viewer = OpenSeadragon({
        id: 'osd',
        tileSources: item['iiif-url'] + '/info.json',
        showNavigationControl: false,
        minZoomImageRatio: 0.2,
        maxZoomPixelRatio: 5,
        homeFillsViewer: (item.fit || this.defaultFit) === 'cover'
      })
      this.viewer.addHandler('canvas-click', (e) => {
        e.preventDefaultAction = true
        this.$store.dispatch('setSelectedImageID', item.id)
        this.$modal.show('image-viewer-modal')
        this.viewer.viewport.panTo(this.center)
        this.viewer.viewport.zoomTo(this.zoom)
      })
      // console.log(this.viewer)
      this.zoom = this.viewer.viewport.getZoom()
      this.center = this.viewer.viewport.getCenter()
      // console.log(`center=${this.center} zoom=${this.zoom}`)
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