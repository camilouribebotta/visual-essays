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
    fit: 'cover',
    containerOrientation: 'portrait',
    imageOrientation: 'portrait',
    center: undefined,
    zoom: undefined,
    drag: false
  }),
  computed: {
    containerStyle() { return { position: 'relative', width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important' } },
  },
  mounted() {
    this.containerOrientation = this.width > this.height ? 'landscape' : 'portrait'
    console.log('OpenSeadragonImageViewer.mounted', this.containerOrientation, this.items)
    this.init()
  },
  methods: {
    init() {
      if (this.viewer) {
        this.viewer.destroy()
      }
      const item = this.items[0]
      this.fit = (item.fit || this.defaultFit) === 'cover' ? 'cover' : 'contain'
      this.viewer = OpenSeadragon({
        id: 'osd',
        tileSources: item['iiif-url'] + '/info.json',
        showNavigationControl: false,
        minZoomImageRatio: 0.2,
        maxZoomPixelRatio: 5,
        homeFillsViewer: this.fit === 'cover'
      })
      this.viewer.world.addHandler('add-item', (e) => {
        const size = this.viewer.world.getItemAt(0).getContentSize()
        this.imageOrientation = size.x > size.y ? 'landscape' : 'portrait'
        console.log(`width=${size.x} height=${size.y} imageOrientation=${this.imageOrientation}`)
      })
      this.viewer.addHandler('canvas-drag-end', (e) => {
        this.drag = true
      })
      this.viewer.addHandler('canvas-click', (e) => {
        e.preventDefaultAction = true
        if (this.drag) {
          this.drag = false
        } else {
          this.$store.dispatch('setSelectedImageID', item.id)
          this.$modal.show('image-viewer-modal')
          if (this.fit === 'cover') {
            if (this.imageOrientation === 'portrait') {
              this.viewer.viewport.fitHorizontally()
            } else {
              this.viewer.viewport.fitVertically()
            }
          } else {
            if (this.imageOrientation === 'portrait') {
              this.viewer.viewport.fitVertically()
            } else {
              this.viewer.viewport.fitHorizontally()
            }
          }
        }
      })
      // console.log(this.viewer)
      // this.zoom = this.viewer.viewport.getZoom()
      // this.center = this.viewer.viewport.getCenter()
      // console.log(`center=${this.center} zoom=${this.zoom}`)
    },
    /*
    getCoverBounds(imageBounds, viewportBounds) {
      var scaleForWidth = imageBounds.width / viewportBounds.width
      var scaleForHeight = imageBounds.height / viewportBounds.height

      var x, y, width, height
      if (scaleForWidth < scaleForHeight) {
        x = imageBounds.x
        width = imageBounds.width
        height = scaleForWidth * viewportBounds.height
        y = (viewportBounds.height - height) / 2
      } else {
        y = imageBounds.y
        height = imageBounds.height
        width = scaleForHeight * viewportBounds.width
        x = (viewportBounds.width - width) / 2
      }
      var newBounds = OpenSeadragon.Rect(x, y, width, height)
      return newBounds
    }
    */
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