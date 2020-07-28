<template>
  <modal name="image-viewer-modal" height="100%" width="100%">
    <v-btn color="red lighten-2" @click="close">Close</v-btn>
    <mirador-image-viewer :items="items" :height="height" :width="width"/>
  </modal>
</template>

<script>
// Uses vue-js-modal:  https://github.com/euvl/vue-js-modal/blob/master/README.md

module.exports = {
  name: 'ImageViewerModal',
  data: () => ({
    items: [],
  }),
  computed: {
    height() { return Math.max(document.documentElement.clientHeight, window.innerHeight * 0.8) - 40 },
    width() { return Math.max(document.documentElement.clientWidth, window.innerWidth * 0.8) },
    selectedImageID() { return this.$store.getters.selectedImageID }
  },
  methods: {
    close() {
      this.$modal.hide('image-viewer-modal')
      this.$store.dispatch('setSelectedImageID', null)
      this.items = []
    },
    getItems(selected) {
      if (this.groups.imageViewer) {
        this.items = this.groups.imageViewer.items.filter(item => item.id === selected)
      } else if (this.groups.plantSpecimenViewer) {
        this.items = this.groups.plantSpecimenViewer.items
          .filter(item => item.specimensMetadata)
          .map(item => item.specimensMetadata.specimens.find(specimen => specimen.id === selected))
      }
    }
  },
  watch: {
    selectedImageID: {
      handler: function (selected) {
        if (selected) {
          this.getItems(selected)
        }
      },
      immediate: true
    }
  }
}
</script>
