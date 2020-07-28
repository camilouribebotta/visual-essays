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
    region: undefined,
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
    console.log('OpenSeadragonImageViewer.mounted', this.width, this.height, this.containerOrientation, this.items)
    this.init()
  },
  methods: {
    parseRegionString(region) {
      const s1 = region.split(':')
      let ints = s1[s1.length-1].split(',').map(v => parseInt(v))
      if (ints.length === 4) {
        if (s1.length === 1 || (s1.length === 2 && (s1[0] === 'px' || s1[0] === 'pixel'))) {
          return this.viewer.viewport.imageToViewportRectangle(new OpenSeadragon.Rect(...ints))
        } else if (s1.length === 2 && (s1[0] === 'pct' || s1[0] === 'percent')) {
          const size = this.viewer.world.getItemAt(0).getContentSize()
          if (size.x > 0 && size.y > 0) {
            return this.viewer.viewport.imageToViewportRectangle(
              Math.round(size.x * ints[0]/100),
              Math.round(size.y * ints[1]/100),
              Math.round(size.x * ints[2]/100), 
              Math.round(size.y * ints[3]/100)
            )
          }
        }
      }
    },
    positionImage() {
      console.log('positionImage', this.region)
      if (this.region) {
        this.viewer.viewport.fitBounds(this.region, true)
      } else if (this.fit === 'cover') {
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
    },
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
        degrees: parseInt(item.rotate || '0'),
        homeFillsViewer: this.fit === 'cover'
      })
      
      if (item.region) {
        this.viewer.addHandler('open', () => {
          this.region = this.parseRegionString(item.region)
          if (this.region) {
            this.positionImage()
          }
        })
      }

      this.viewer.world.addHandler('add-item', (e) => {
        this.region = item.region ? this.parseRegionString(item.region) : null
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
          this.positionImage()
        }
      })
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