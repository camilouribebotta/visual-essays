<template>
  <v-card id="image-viewer" :style="`height:${viewport.height}px`">
    <v-card-title></v-card-title>
    <v-container fluid>
      <v-row dense>
        <v-col
          v-for="image in images"
          :key="image.id"
          :cols="image.cols || 6"
        >
          <v-card>
            <div :id="image.id" :style="`width:100%; height:${(image.cols || 6) * 50}px`"/>
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
  <!--
  <div ref="imageViewer" id="imageViewer">
    <ul class="listHorizontal">
      <li v-for="image in images" :key="image.id">
        <h3>{{ image.title }}</h3>
        <div 
          :id="image.id" 
          class="image" 
          :style="style"
        />
      </li>
    </ul>
  </div>
  -->
</template>

<script>
import axios from 'axios'
import OpenSeadragon from 'openseadragon'
export default {
  name: 'ImageViewer',
  data: () => ({}),
  computed: {
    images() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'image') },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
    style() { return {
      width: '100%',
      height: '300px'
    }}
  },
  mounted() {
    this.images.forEach((image) => {
      const url = 'https://deepzoomapi-atjcn6za6q-uc.a.run.app/generate?url=' + image.url
      console.log(url)
      let dziURL = axios.get('https://deepzoomapi-atjcn6za6q-uc.a.run.app/generate?url=' + image.url).then((resp) => {
        let viewer = OpenSeadragon({
          id: image.id,
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
    })
  }
}

</script>

<style scoped>
  #image-viewer {
    background-color: #ddd;
    padding: 3px 10px 3px 3px;
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