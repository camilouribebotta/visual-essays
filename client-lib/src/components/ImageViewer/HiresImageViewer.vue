<template>
  <div>
    <v-dialog 
      v-if="isOpen"
      v-model="isOpen"
      @click:outside="close"
      :width="width"
      :height="height"
    >
      <v-card>
        <v-card-title v-html="img.caption"/>
        <div :style="`border:1px solid #eee; width:${width}px; height:${height}px;`" id="img"/>
        <v-card-actions>
          <v-btn @click="close">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import OpenSeadragon from 'openseadragon'

export default {
  name: 'hires-image-viewer',
  props: {
    img: { type: Object, default: () => undefined }
  },
  data: () => ({
    isOpen: false,

  }),
  computed: {
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
    scale() { return this.viewport.height * .9 / this.img.height },
    width() { return this.img.width * this.scale },
    height() { return this.img.height * this.scale - 120}
  },
  methods: {
    loadImage() {
      console.log(`src=${this.img.src} width=${this.img.width} height=${this.img.height}`)
      const url = `https://deepzoomapi-atjcn6za6q-uc.a.run.app/generate?url=${this.img.src}`
      console.log(url)
      let dziURL = axios.get(url).then((resp) => {
        let viewer = OpenSeadragon({
          id: 'img',
          tileSources: {
            Image: resp.data.data
          },
          buildPyramid: false,
          showNavigationControl: false,
          maxZoomLevel: 5,
          showNavigator: true,
          homeFillsViewer: true,
          //navigatorId: 'image-navigator',
          //toolbar: 'image-toolbar',
          //zoomInButton: 'image-toolbar-zoomin',
          //zoomOutButton: 'image-toolbar-zoomout',
          //homeButton: 'image-toolbar-reset',
          //fullPageButton: 'image-toolbar-fullscreen'
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
    },
    close() {
      this.isOpen = false
    }
  },
  watch: {
    img() {
      if (this.img) {
        this.loadImage()
        this.isOpen = true
      } else {
        this.isOpen = false
      }
    }
  }
}
</script>

<style scoped>
  .v-card__actions {
    padding: 3px;
  }
</style>
