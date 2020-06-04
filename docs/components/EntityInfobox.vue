<template>
  <div class="entity-infobox">
    <div class="entity-image-holder" v-if="imageSrc" :style="{backgroundSize: imageFit, backgroundImage: 'url(' + imageSrc + ')'}"></div>
    <h3 class="entity-title" primary-title v-html="title"></h3>
    <div class="subtitle">{{ description }}</div>
    <div class="entity-description" v-html="html"></div>
    <a :href="entity.wikipedia_page" target="_blank" >Source</a>
  </div>
</template>

<script>

module.exports = {
  name: 'entity-infobox',
  props: {
    eid: { type: String, default: undefined },
    imageFit: { type: String, default: 'contain' }
    /* imageFit:
       fill = stretched to fit box
       contain = maintain its aspect ratio, scaled fit within the element’s box, letterboxed if needed
       cover = fills entire box, maintains aspect ration, clipped to fit
       none = content not resized
       scale-down = same as none or contain, whichever is smaller
    */
  },
  data: () => ({
    requested: new Set()
  }),
  computed: {
    entity () { return this.$store.getters.items.find(entity => entity.eid && entity.eid === this.eid) || {} },
    entityInfo () { return this.entity['summary info'] },
    title () { return this.entityInfo && this.entityInfo.displaytitle || this.entity.label || this.entity.title },
    description () { return this.entityInfo ? this.entityInfo.description : this.entity.description },
    thumbnail () { return this.entityInfo && this.entityInfo.thumbnail ? this.entityInfo.thumbnail.source : null },
    imageSrc () { return this.thumbnail ?  this.thumbnail : this.entity.images ? this.entity.images[0] : null },
    html () { return this.entityInfo ?  this.entityInfo.extract_html : null },
    context() { return this.$store.getters.context },
    apiBaseURL() { return window.location.origin }
  },
  mounted() {
    this.getSummaryInfo()
  },
  methods: {
    getEntity(eid, context) {
      const url = `${this.apiBaseURL}/entity/${eid}` + (context ? `?context=${context}` : '')
      return fetch(url).then(resp => resp.json())
    },
    getSummaryInfo() {
      if (this.entity.eid && this.entity['summary info'] === undefined && !this.requested.has(this.entity.eid)) {
        this.requested.add(this.entity.eid)
        this.getEntity(this.entity.eid, this.context)
          .then((updated) => {
            if (!updated['summary info']) {
              updated['summary info'] = null
            }
            updated.id = this.entity.eid
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

  .source-link {
    position: absolute;
    float: left;
    padding-left: 8px;
  }

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
