<template>
  <div ref="essay" id="essay" v-html="html"/>
</template>

<script>
import { elemIdPath, itemsInElements, groupItems } from '../utils'

export default {
  name: 'essay',
  data: () => ({
    paragraphs: {}
  }),
  computed: {
    html() { return this.$store.getters.essayHTML },
    debug() { return this.$store.getters.debug },
    viewportWidth() { return this.$store.getters.width },
    allItems() { return this.$store.getters.items }
  },
  mounted() {
    groupItems(this.allItems)
    this.$nextTick(() => this.init())
    if (window.location.hash) {
      this.scrollTo(window.location.hash.slice(1))
    }
  },
  methods: {
    init() {
      this.findContent()
      this.linkTaggedItems()
      this.addFootnotesHover()

      // Setup ScrollMagic (https://scrollmagic.io/)
      let prior
      Array.from(document.body.querySelectorAll('p')).filter(elem => elem.id).forEach((para) => {
        para.title = elemIdPath(para.id).join(',')
        this.paragraphs[para.id] = {
          prior, 
          top: para.offsetTop,
          items: itemsInElements(elemIdPath(para.id), this.allItems)
        }
        prior = para.id
        const scene = this.$scrollmagic.scene({
          triggerElement: `#${para.id}`,
          triggerHook: 0.25
        })
        .on('enter', (e) => {
          this.setActiveElements(para.id)
        })
        .on('leave', (e) => {
          if (e.scrollDirection === 'REVERSE' || e.scrollDirection === 'PAUSED') {
            this.setActiveElements(this.paragraphs[para.id].prior)
          }
        })
        if (this.debug) {
          scene.addIndicators()
        }
        this.$scrollmagic.addScene(scene)

      })
    },
    setActiveElements(elemId) {
      this.$store.dispatch('setActiveElements', elemIdPath(elemId))
    },
    getParagraphs(elem) {
      const paragraphs = []
      if (elem) {
        Array.prototype.slice.call(elem.getElementsByTagName('p')).forEach((para) => {
          if (para.id) {
            para.title = `${para.id} (${para.offsetTop})`
            paragraphs.push({
              type: 'paragraph',
              id: para.id,
              top: para.offsetTop,
              bottom: para.offsetTop + para.offsetHeight,
              items: this.itemsPartOf(para.id),
            })
          }
        })
      }
      return paragraphs
    },
    findContent() {
      const content = this.getParagraphs(document.getElementById('essay'))
      for (let i = 1; i < 9; i++) {
        document.body.querySelectorAll(`h${i}`).forEach((heading) => {
          const sectionElem = heading.parentElement
          const sectionId = sectionElem.attributes.id.value
          //sectionElem.title = `${sectionId} (${sectionElem.offsetTop})`
          const section = {
            id: sectionId,
            level: i,
            title: heading.innerHTML,
            top: sectionElem.offsetTop,
            bottom: sectionElem.offsetTop + sectionElem.offsetHeight,
            items: this.itemsPartOf(sectionId),
            paragraphs: this.getParagraphs(sectionElem)
          }
          content.push(section)
        })
      }
      console.log('content', content)
      this.$store.dispatch('setContent', content)
    },
    itemsPartOf(elemId) {
      const items = []
      this.$store.getters.items.forEach((item) => {
        if (item.found_in.has(elemId) || item.tagged_in.has(elemId) ||
            (item.type !== 'entity' && item.tagged_in.has('essay'))) {
          items.push(item)
        }
      })
      return items
    },
    scrollTo(elemid) {
      const elem = document.getElementById(elemid)
      if (elem) {
        window.scrollTo(0, elem.offsetTop)
      }
    },
    addFootnotesHover() {
      document.querySelectorAll('.footnote-ref').forEach((fn) => {
        fn.addEventListener('mouseover', (e) => {
          const fnId = e.toElement.hash.slice(1)
          const fnHTML = document.getElementById(fnId).innerHTML
          // console.log(`footnote: id=${fnId} html="${fnHTML}"`)
        })
      })
    },
    linkTaggedItems() {
      document.querySelectorAll('.tagged').forEach((item) => {
        item.addEventListener('click', (e) => {
          const elemId = e.target.attributes['data-itemid'].value
          this.$store.dispatch('setSelectedItemID', elemId)
        })
      })
    }
  }
}
</script>

<style>

  #essay {
    height: 100%;
  }

</style>