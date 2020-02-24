<template>
  <div>
    <v-dialog v-if="selectedItemID" v-model="isOpen" @click:outside="clearSelectedItemID" width="500">
      <v-card class="infobox">
          <entity-infobox :qid="selectedItemID"/>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            text
            @click="clearSelectedItemID"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>      
    </v-dialog>
  </div>
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

  div.v-card__text div p {
    width: 95%;
    padding: 0;
    margin: 0;
  }

  img {
    /* object-fit:
       fill = stretched to fit box
       contain = maintain its aspect ratio, scaled fit within the element’s box, letterboxed if needed
       cover = fills entire box, maintains aspect ration, clipped to fit
       none = content not resized
       scale-down = same as none or contain, whichever is smaller
    */
    object-fit: cover; 
    width: 150px;
    height: 150px;
    padding: 2px 10px 2px 0;
    float: left;
    vertical-align: top;
  }

  .subtitle {
    line-height: 1em;
    margin-bottom: 8px;
    font-weight: bold;
    font-size: 1.1em;
  }

</style>
