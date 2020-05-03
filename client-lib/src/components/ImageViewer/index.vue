<template>
  <div id="image-viewer" >
    <div id="image-viewer-controls" @click="click()">
      <v-radio-group
        v-if="images.length > 1"
        id="image-viewer-mode-control"
        :value="mode"
        row
        dense
        :hide-details="true"
        color="primary"
      >
        <v-radio label="Gallery" value="gallery"></v-radio>
        <v-radio label="Compare" value="cards"></v-radio>
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
  props: {
    initialMode: { type: String, default: 'gallery' }
  },
  data: () => ({
    mode: 'gallery',
  }),
  computed: {
    images() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'image') }
  },
  methods: {
    click() {
      this.mode = this.mode === 'cards' ? 'gallery' : 'cards'
    }
  },
  watch: {
    initialMode: {
      handler: function (mode) {
        this.mode = this.initialMode || 'gallery'
      },
      immediate: true
    }
  }
}
</script>

<style>

  #image-viewer-controls {
    z-index: 300;
    position: absolute;
    height: 36px;
    top: 0px;
    left: 16px;
    /* background-color: #fbfdff; */
    /*border-radius: 4px;*/
    /*box-shadow: 0 1px 5px rgba(0,0,0,0.65);*/
    padding: 20px 10px !important;
    height: 70px !important;
  }

  #image-viewer-mode-control {
    position: relative;
    top: -10px;
    background: white;
    padding: 8px;
    border-radius: 8px;
    opacity: 1.0;
  }

  .v-application .accent--text {
    color: #1D5BC2 !important;
  }

  .v-input {
    margin: 2px 0 0 4px !important;
  }

  .component {
    position: relative;
  }

</style>