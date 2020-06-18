<template>
  <modal name="mirador" height="100%" width="100%">
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
  },
  methods: {
    close() {
      this.$modal.hide('mirador')
    },
    getItems() {
      if (this.groups.imageViewer) {
        this.items = this.groups.imageViewer.items
      } else if (this.groups['plant-specimen']) {
        const promises = this.groups['plant-specimen'].items
          .filter(item => item.specimensData && item.specimensData.specimens && item.specimensData.specimens.length > 0)
          .map(item => item.specimensData.specimens[0].manifestId)
        Promise.all(promises)
          .then(manifests => {
            this.items = manifests.map(manifest => {return { manifestId: manifest['@id'] }})
          })
      }
    }
  },
  watch: {
    groups: {
      handler: function () {
        this.getItems()
      },
      immediate: true
    }
  }
}
</script>
