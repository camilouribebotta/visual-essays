<template>
  <div id="image-viewer" >
    <component 
      v-bind:is="mode === 'iiif' ? 'openSeadragonImageViewer' : 'staticImageViewer'"
      :width="width" :height="height" :seq="seq" :items="items" :default-fit="defaultFit"
    ></component>
  </div>
</template>

<script>

/*
*/

module.exports = {
  name: 'ImageViewer',
  props: {
    seq: {type: Number, default: 1},
    items: Array,
    width: Number,
    height: Number,
    initialMode: { type: String, default: 'iiif' },
    defaultFit: {type: String, default: 'cover'}
  },
  data: () => ({
    mode: 'static',
  }),
  mounted() {
    console.log(`ImageViewer.mounted: seq=${this.seq} initialMode=${this.initialMode}`)
  },
  watch: {
    items: {
      handler: function () {
        const itemWithModeDefined = this.items.find(item => item.iiif || item.static)
        const requestedMode = itemWithModeDefined
          ? itemWithModeDefined.static
            ? 'static'
            : 'iiif'
          : undefined
        this.mode = this.items.length > 1
          ? 'static'
          : requestedMode || this.initialMode
        console.log(`ImageViewer items=${this.items.length} requestedMode=${requestedMode} mode=${this.mode}`, this.items)
      },
      immediate: true
    }
  }
}
</script>