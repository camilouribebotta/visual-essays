<template>
  <div id="image-viewer">
    <v-radio-group id="image-viewer-mode-control" v-model="mode" row>
      <v-radio label="Gallery" value="gallery"></v-radio>
      <v-radio label="Cards (compare mode)" value="cards"></v-radio>
    </v-radio-group>
    <component v-bind:is="mode"/>
  </div>
</template>

<script>
import CardsImageViewer from './CardsImageViewer'
import GalleryImageViewer from './GalleryImageViewer'

export default {
  name: 'ImageViewer',
  components: {
    'cards': CardsImageViewer,
    'gallery': GalleryImageViewer
  },
  data: () => ({
    mode: 'gallery',
  })
}
</script>

<style>
  #image-viewer-mode-control {
    margin-left: 10px !important;
    height: 15px !important;
  }
</style>