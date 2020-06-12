<template>
  <modal name="mirador" height="100%" width="100%">
    <v-btn color="red lighten-2" @click="close">Close</v-btn>
    <mirador-image-viewer :items="items" :height="height" :width="width"/>
  </modal>
</template>

<script>
// Uses vue-js-modal:  https://github.com/euvl/vue-js-modal/blob/master/README.md

const useFor = new Set(['imageViewer', 'plant-specimen'])

module.exports = {
  name: 'ImageViewerModal',
  computed: {
    height() { return Math.max(document.documentElement.clientHeight, window.innerHeight * 0.8) - 40 },
    width() { return Math.max(document.documentElement.clientWidth, window.innerWidth * 0.8) },
    items() {
      const matchedGroupName = Object.keys(this.groups).find(group => useFor.has(group))
      return matchedGroupName ? this.groups[matchedGroupName].items : []
    }
  },
  methods: {
    close() {
      this.$modal.hide('mirador')
    }
  }
}
</script>
