<template>
  <v-dialog v-if="selectedItemID" v-model="isOpen" @click:outside="clearSelectedItemID" width="500">
    <v-btn small icon color="white" class="infobox-close" @click="clearSelectedItemID">
      <v-icon>mdi-close</v-icon>
    </v-btn>
    <v-card class="infobox">
      <entity-infobox :qid="selectedItemID"></entity-infobox>
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
    selectedItemId () { return this.$store.getters.selectedItemId },
  },
  methods: {
    clearSelectedItemID() {
      this.$store.dispatch('setSelectedItemID')
    }
  },
  watch: {
    selectedItemID(qid) {
      this.isOpen = qid !== null
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
