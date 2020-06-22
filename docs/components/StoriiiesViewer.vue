<template>
  <div id="osd-viewer" :style="containerStyle">
    <button id="caption-box-show" class="button caption-box-show">Show info box</button>
    <div id="caption-box" class="caption-box">
        <div class="caption-box__header">
            <button id="caption-box-hide" class="button button--toggle caption-box-hide">Hide info box</button>
            <div class="caption-box__controls">
                <button id="previous" class="button button__previous">Previous</button>
                <button id="next" class="button button__next">Next</button>
            </div>
        </div>
        <div id="annotation">
        </div>
    </div>
    <div id="osd-viewer"></div>
  </div>
</template>
<script>

module.exports = {
  name: 'StoriiiesViewer',
  props: { items: Array, width: Number, height: Number },
  computed: {
    containerStyle() { return { position: 'relative', width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important' } },
  },
  mounted() {
    var manifest = `https://jqz7t23pp9.execute-api.us-east-1.amazonaws.com/dev/manifest/${this.items[0].id}/manifest.json`
    fetch('https://storiiies.cogapp.com/manifestJSON?manifest=' + manifest).then(resp => resp.json()).then(data => initialiseViewer(data))
  }
}
</script>
