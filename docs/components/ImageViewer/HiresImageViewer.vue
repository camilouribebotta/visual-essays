<template>
  <div>
    <v-dialog v-model="isOpen" @click:outside="close">
      <v-card dark>
        <v-card-title v-html="img.caption" class="card-title"></v-card-title>
        <v-card-actions class="close-button">
          <v-btn @click="close" color="primary">Exit</v-btn>
        </v-card-actions>
        <v-card-text>
          <div id="img" :style="`width:${width}px; height:${height}px;`"></div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
// import OpenSeadragon from 'openseadragon'

module.exports = {
  name: 'hires-image-viewer',
  props: {
    img: { type: Object, default: () => undefined }
  },
  data: () => ({
    isOpen: false,
  }),
  computed: {
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
    scale() { return this.viewport.height * .98 / this.img.height },
    width() { return this.img.width * this.scale },
    height() { return this.img.height * this.scale - 150}
  },
  methods: {
    loadImage() {
      // const url = `https://lwljoqf02g.execute-api.us-east-1.amazonaws.com/prod/generate?url=${encodeURIComponent(this.img.src)}`
      const url = `https://deepzoomapi-atjcn6za6q-uc.a.run.app/generate?url=${this.img.src}`
      let dziURL = fetch(url).then(resp => resp.json()).then((resp) => {
        let viewer = OpenSeadragon({
          id: 'img',
          tileSources: {
            Image: resp.data
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
        this.isOpen = true
        this.loadImage()
      } else {
        this.isOpen = false
      }
    }
  }
}
</script>

<style scoped>
  .v-overlay {
    opacity: 100 !important;
  }

  .theme--dark.v-sheet {
    background-color: black;
  }

  .card-title {
    padding-top: 16px !important;
  }

  .v-card__title {
    background-color: #fff;
    padding-left: 16px !important;
    border-bottom: 1px solid #acb0bc;
    color: #000;
  }

  .close-button {
    display: inline-block;
    position: absolute;
    top: 3px;
    right: 0;

  }
</style>
