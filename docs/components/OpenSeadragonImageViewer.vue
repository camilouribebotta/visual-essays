<template>
  <div id="osd" :style="containerStyle">OpenSeadragon Image Viewer</div>
</template>
<script>

module.exports = {
  name: 'OpenSeadragonImageViewer',
  props: {
    items: Array,
    width: Number,
    height: Number
  },
  data: () => ({}),
  computed: {
    containerStyle() { return { position: 'relative', width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important' } },
  },
  mounted() {
      console.log('OpenSeadragonImageViewer.mounted', this.items)
      OpenSeadragon({
        id:            'osd',
        prefixUrl:     '/openseadragon/images/',
        sequenceMode:  true,
        tileSources:   [
            "https://libimages1.princeton.edu/loris/pudl0001%2F4609321%2Fs42%2F00000001.jp2/info.json",
            "https://libimages1.princeton.edu/loris/pudl0001%2F4609321%2Fs42%2F00000002.jp2/info.json",
            "https://libimages1.princeton.edu/loris/pudl0001%2F4609321%2Fs42%2F00000003.jp2/info.json",
            "https://libimages1.princeton.edu/loris/pudl0001%2F4609321%2Fs42%2F00000004.jp2/info.json",
            "https://libimages1.princeton.edu/loris/pudl0001%2F4609321%2Fs42%2F00000005.jp2/info.json",
            "https://libimages1.princeton.edu/loris/pudl0001%2F4609321%2Fs42%2F00000006.jp2/info.json",
            "https://libimages1.princeton.edu/loris/pudl0001%2F4609321%2Fs42%2F00000007.jp2/info.json"
        ]
    })
  }
}
</script>

<style>
</style>