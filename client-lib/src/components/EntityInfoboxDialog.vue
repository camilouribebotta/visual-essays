<template>
  <div>
    <v-dialog v-model="isOpen" @click:outside="setSelectedEntityQID(null)" width="500">
      <v-card class="entity-infobox-dialog" v-if="entity">
        <v-card-title class="headline grey lighten-2" primary-title v-html="title"/>
        <v-card-text>
          <img v-if="imageSrc" :src="imageSrc">
          <div class="subtitle">{{ description }}</div>
          <div v-html="html"/>
        </v-card-text>
        <v-divider/>
        <v-card-actions>
          <v-spacer/>
          <v-btn color="primary" text @click="setSelectedEntityQID(null)">Dismiss</v-btn>
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
    selectedEntityQID () { return this.$store.getters.selectedEntityQID },
    entity () { return this.$store.getters.items.find(entity => entity.qid === this.selectedEntityQID) || {} },
    entityInfo () { return this.entity['summary info'] },
    title () { return this.entityInfo ? this.entityInfo.displaytitle : this.entity.label },
    description () { return this.entityInfo ? this.entityInfo.description : this.entity.description },
    thumbnail () { return this.entityInfo && this.entityInfo.thumbnail ? this.entityInfo.thumbnail.source : null },
    imageSrc () { return this.thumbnail ?  this.thumbnail : this.entity.images ? this.entity.images[0] : null },
    html () { return this.entityInfo ?  this.entityInfo.extract_html : null }
  },
  methods: {
    setSelectedEntityQID(arg) {
      const qid = arg && arg.target ? arg.target.attributes['data-entity'].value : arg
      const selectedEntity = qid === this.selectedEntityQID ? null : qid
      this.$store.dispatch('setSelectedEntityQID', selectedEntity)
    }
  },
  watch: {
    selectedEntityQID(qid) {
      this.isOpen = qid !== null
    }
  }
}
</script>

<style scoped>

  .entity-infobox-dialog .v-card__text {
    min-height: 165px;
    padding-bottom: 0 !important;
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
