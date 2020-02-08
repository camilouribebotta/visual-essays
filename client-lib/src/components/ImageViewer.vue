<template>
  <div ref="imageViewer" id="imageViewer">
    <ul class="listHorizontal">
      <li v-for="image in images" :key="image.id">
        <h3>{{ image.title }}</h3>
        <div :id="image.id" class="image" :style="`width:${viewport.height*0.3}px; height:${viewport.height*0.40}px;`"></div>
      </li>
    </ul>
  </div>
</template>

<script>
var openseadragon = require('openseadragon');
export default {
  name: 'ImageViewer',
  data: () => ({}),
  computed: {
    images() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'image') },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} }
  },
  mounted() {
    this.images.forEach((image) => {
      let dziURL = this.axios.get('https://deepzoomapi-atjcn6za6q-uc.a.run.app/generate?url=' + image.url).then((resp) => {
        let viewer = OpenSeadragon({
          id: image.id,
          tileSources: {
            Image: resp.data.data
          },
          buildPyramid: false,
          showNavigationControl: false
        })
        if (image.region !== undefined && image.region[2] != 0 && image.region[0] !== undefined) {
            // console.log("Editing initial region")
            let region = image.region
            viewer.addHandler("open", function(){
                let rect = viewer.viewport.imageToViewportRectangle(region[0], region[1], region[2]-region[0], region[3]-region[1]);
                viewer.viewport.fitBounds(rect, true);
            });
        }
      })
    })
  }
}

</script>

<style>
  h3 {
    font-size: 14pt;
    color: black;
    margin-bottom: 6px;
  }
  .listHorizontal {
    margin-top: 12px;
    display: flex;
    justify-content: space-around;
    color: #b6d8cf;
    font-size:30px;
    text-transform: uppercase;
    list-style: none;
  }
</style>