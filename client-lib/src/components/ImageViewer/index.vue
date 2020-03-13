<template>
  <div id="image-viewer">
    <div id="image-viewer-controls">
      <v-radio-group v-if="images.length > 1" id="image-viewer-mode-control" v-model="mode" row>
        <v-radio label="Gallery" value="gallery"></v-radio>
        <v-radio label="Cards (compare mode)" value="cards"></v-radio>
      </v-radio-group>
    </div>
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
  }),
  computed: {
    images() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'image') }
  }
}
</script>

<style>
  #image-viewer-controls {
    margin-left: 10px !important;
    height: 50px !important;
  }
  .v-input {
    margin: 6px 0 0 6px !important;
  }
</style>