<template>
  <div>
    <v-card id="cards-image-viewer" :style="`height:${viewport.height}px; padding:${isHorizontal ? 0 : 8}px !important;`">
      <v-container fluid style="margin-top:34px;">
        <v-row dense>
          <v-col
            v-for="image in images"
            :key="image.id"
            :cols="image.cols || 6"
            :style="`padding:${isHorizontal ? 0 : 8}px !important;`"
          >
            <v-card>
              <div :id="image.id" :style="`width:100%; height:${isHorizontal ? viewport.height/2 : (image.cols || 6) * 50}px`"/>
              <!-- 
              <v-card-actions>
                <v-spacer/>
                <v-btn icon><v-icon>mdi-heart</v-icon></v-btn>
                <v-btn icon><v-icon>mdi-bookmark</v-icon></v-btn>
                <v-btn icon><v-icon>mdi-share-variant</v-icon></v-btn>
              </v-card-actions>
              -->
              <v-card-title v-text="image.title">
              </v-card-title>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-card>
    <hires-image-viewer :img="img" />
  </div>
</template>

<script>
// import OpenSeadragon from 'openseadragon'

module.exports = {
  name: 'CardsImageViewer',
  data: () => ({
    currentId: undefined,
    img: {}
  }),
  computed: {
    images() { return this.$store.getters.itemsInActiveElements.filter(item => item.tag === 'image') },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
    isHorizontal() { return this.$store.getters.layout[0] === 'h' },
  },
  mounted() {
    this.images.forEach((image) => {
      // const url = image.url
      // const url = `https://lwljoqf02g.execute-api.us-east-1.amazonaws.com/prod/generate?url=${image.url}`
      const url = `https://deepzoomapi-atjcn6za6q-uc.a.run.app/generate?url=${image.url}`
      let dziURL = fetch(url).then(resp => resp.json()).then((resp) => {
        let viewer = OpenSeadragon({
          id: image.id,
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
    })
  }
}

</script>

<style scoped>

  #cards-image-viewer {
    border-radius: 0;
    background-color: #f5f5f5;
    padding: 8px;
    overflow-y: scroll;
  }

  .v-card__title {
    padding: 6px 12px;
    font-size: 1.0rem;
    line-height: 1.2rem;
    height: 50px;
    word-break: normal !important;
  }

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