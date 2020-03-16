<template>
  <div id="image-viewer">
    <div id="image-viewer-controls">
      <v-radio-group
              v-if="images.length > 1"
              id="image-viewer-mode-control"
              v-model="mode"
              row
              dense
              hide-details=true
      >
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
    z-index: 300;
    position: fixed;
    top: 16px;
    left: 16px;
    background-color: #fbfdff;
    border-radius: 4px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.65);
    height: 36px;
  }

  .v-input {
    margin: 2px 0 0 4px !important;
  }

  .component {
    position: relative;
  }

</style>