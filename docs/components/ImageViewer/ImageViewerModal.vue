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
      console.log(this.groups)
      if (this.groups.image) {
        this.items = this.groups.image.items
      } else if (this.groups.plantSpecimen) {
        console.log('plantSpecimens', this.groups.plantSpecimen)
        this.items = this.groups.plantSpecimen.items
          .filter(item => item.specimensMetadata)
          .map(item => item.specimensMetadata.specimens[0])
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
