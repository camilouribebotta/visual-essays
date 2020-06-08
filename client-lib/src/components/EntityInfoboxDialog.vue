<template>
  <v-dialog v-if="selectedItemID" v-model="isOpen" @click:outside="clearSelectedItemID" width="500">
    <v-btn small icon color="white" class="infobox-close" @click="clearSelectedItemID">
      <v-icon>mdi-close</v-icon>
    </v-btn>
    <v-card class="infobox">
      <entity-infobox :eid="eid"></entity-infobox>
    </v-card>
  </v-dialog>
</template>

<script>

export default {
  name: 'entity-infobox-dialog',
  data: () => ({
    isOpen: false
  }),
  computed: {
    selectedItemID () { return this.$store.getters.selectedItemID },
    selectedItem () { return this.$store.getters.items.find(entity => entity.id === this.selectedItemID) || {} },
    eid() { console.log(this.selectedItemID, this.selectedItem); return this.selectedItem.eid }
  },
  methods: {
    clearSelectedItemID() {
      this.$store.dispatch('setSelectedItemID')
    }
  },
  watch: {
    selectedItemID(eid) {
      this.isOpen = eid !== null
    }
  }
}
</script>

<style scoped>

  .infobox-close {
    background-color: #1D5BC2;
    border: 1px solid white;
    z-index: 1000;
    position: absolute;
    margin-top: -10px;
    margin-left: 480px;
  }

</style>
