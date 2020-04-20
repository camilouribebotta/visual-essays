<template>
  <div class="entity-infobox">
    <div class="entity-image-holder" v-if="imageSrc" :style="{backgroundImage: 'url(' + imageSrc + ')'}">
    </div>

    <h3 class="entity-title" primary-title v-html="title"/>
    <div class="subtitle">{{ description }}</div>
    <div class="entity-description" v-html="html"/>
    <a :href="entity.wikipedia_page" target="_blank" >Source</a>
  </div>
</template>

<script>
import { get_entity } from '../api'

export default {
  name: 'entity-infobox',
  props: {
    qid: { type: String, default: undefined }
  },
  data: () => ({
    requested: new Set()
  }),
  computed: {
    entity () { return this.$store.getters.items.find(entity => entity.qid && entity.qid === this.qid) || {} },
    entityInfo () { return this.entity['summary info'] },
    title () { return this.entityInfo && this.entityInfo.displaytitle || this.entity.label || this.entity.title },
    description () { return this.entityInfo ? this.entityInfo.description : this.entity.description },
    thumbnail () { return this.entityInfo && this.entityInfo.thumbnail ? this.entityInfo.thumbnail.source : null },
    imageSrc () { return this.thumbnail ?  this.thumbnail : this.entity.images ? this.entity.images[0] : null },
    html () { return this.entityInfo ?  this.entityInfo.extract_html : null },
    context() { return this.$store.getters.context }
  },
  mounted() {
    console.log(this.entity.wikipedia_page);
    this.getSummaryInfo()
  },
  methods: {
    getSummaryInfo() {
      if (this.entity.qid && this.entity['summary info'] === undefined && !this.requested.has(this.entity.qid)) {
        this.requested.add(this.entity.qid)
        get_entity(this.entity.qid, this.context)
          .then((updated) => {
            if (!updated['summary info']) {
              updated['summary info'] = null
            }
            updated.id = this.entity.qid
            this.$store.dispatch('updateItem', updated)
          })
      }
    }
  },
  watch: {
    qid: {
      handler: function (value, prior) {
        console.log('EntityInfobox.watch.qid', value)
      },
      immediate: true
    },
    entity() {
      this.getSummaryInfo()
    }
  }
}
</script>

<style scoped>

  .entity-infobox {
    align-items: left;
  }

  .entity-infobox .v-card__text {
    height: 100%;
    min-height: 165px;
    padding-bottom: 0 !important;
  }

  .entity-title {
    padding: 0;
    margin-bottom: 8px;
  }

  .entity-image-holder {
    width: 100%;
    height: 250px;
    background-color: #7F828B;
    background-size: cover;
    background-position: center;
    margin-bottom: 16px;
  }

  .subtitle {
    line-height: 1em;
    margin-bottom: 16px;
    font-size: 16px;
  }



</style>
