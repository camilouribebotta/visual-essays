<template>
  <v-card class="entity-infobox">
    <v-card-title primary-title v-html="title"/>
    <v-card-text>
      <img v-if="imageSrc" :src="imageSrc">
      <div class="subtitle">{{ description }}</div>
      <div style="text-align: left;" v-html="html"/>
    </v-card-text>
  </v-card>
</template>

<script>
import { get_entity } from '../api'

export default {
  name: 'entity-infobox',
  props: {
    qid: { type: String }
  },
  data: () => ({
    requested: new Set()
  }),
  computed: {
    entity () { return this.$store.getters.items.find(entity => entity.qid === this.qid) || {} },
    entityInfo () { return this.entity['summary info'] },
    title () { return this.entityInfo && this.entityInfo.displaytitle || this.entity.label || this.entity.title },
    description () { return this.entityInfo ? this.entityInfo.description : this.entity.description },
    thumbnail () { return this.entityInfo && this.entityInfo.thumbnail ? this.entityInfo.thumbnail.source : null },
    imageSrc () { return this.thumbnail ?  this.thumbnail : this.entity.images ? this.entity.images[0] : null },
    html () { return this.entityInfo ?  this.entityInfo.extract_html : null },
    context() { return this.$store.getters.context }
  },
  mounted() {
    this.getSummaryInfo()
  },
  methods: {
    getSummaryInfo() {
      if (this.entity.qid && this.entity['summary info'] === undefined && !this.requested.has(this.entity.qid)) {
        this.requested.add(this.entity.qid)
        get_entity(this.entity.qid, this.context)
          .then((updated) => {
            if (!updated['summary info']) {
              updated['summary info'] = NULL
            }
            updated.id = this.entity.qid
            this.$store.dispatch('updateItem', updated)
          })
      }
    }
  },
  watch: {
    entity() {
      this.getSummaryInfo()
    }
  }
}
</script>

<style scoped>

  .entity-infobox .v-card__text {
    height: 100%;
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
    font-size: 1.2em;
  }

</style>
