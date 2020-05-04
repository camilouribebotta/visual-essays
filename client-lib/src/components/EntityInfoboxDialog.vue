<template>
  <div>
    <v-dialog v-if="selectedItemID" v-model="isOpen" @click:outside="clearSelectedItemID" width="500">
        <v-btn
                small
                color="white"
                class="infobox-close"
                icon
                @click="clearSelectedItemID">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      <v-card class="infobox">
        <entity-infobox :qid="selectedItemID"/>
        <v-card-actions>
          <v-spacer></v-spacer>
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

  .source-link {
    position: absolute;
    float: left;
    padding-left: 8px;
  }

  .infobox-close {
    background-color: #1D5BC2;
    border: 1px solid white;
    z-index: 1000;
    position: absolute;
    margin-top: -10px;
    margin-left: 480px;
  }


</style>
