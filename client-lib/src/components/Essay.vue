<template>
  <div ref="essay" id="essay" v-html="html"/>
</template>

<script>
import { elemIdPath, itemsInElements, groupItems, eqSet } from '../utils'

export default {
  name: 'essay',
  data: () => ({
    paragraphs: {},
    scenes: []
  }),
  computed: {
    html() { return this.$store.getters.essayHTML },
    debug() { return this.$store.getters.debug },
    viewportWidth() { return this.$store.getters.width },
    allItems() { return this.$store.getters.items },
    contentStartPos() { return this.$store.getters.contentStartPos },
    activeElements() { return this.$store.getters.activeElements },
    triggerHook() { return (this.contentStartPos + this.$store.getters.triggerOffset) / this.$store.getters.height },
  },
  created() {

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
          triggerHook: this.triggerHook,
        })
        .on('enter', (e) => {
          this.setActiveElements(para.id)
        })
        .on('leave', (e) => {
          //if (e.scrollDirection === 'REVERSE' || e.scrollDirection === 'PAUSED') {
            this.setActiveElements(this.paragraphs[para.id].prior)
          //}
        })
        if (this.debug) {
          scene.addIndicators({indent: this.viewportWidth/2})
        }
        this.$scrollmagic.addScene(scene)
        this.scenes.push(scene)
      })
      this.setActiveElements(Array.from(document.body.querySelectorAll('p')).find(elem => elem.id).id)
    },
    setActiveElements(elemId) {
      if (elemId) {
        const newActiveElements = elemIdPath(elemId)
        if (!eqSet(new Set(this.activeElements), new Set(newActiveElements))) {
          if (document.getElementById('triangle')) {
            document.getElementById('triangle').remove();
          }
          this.$store.dispatch('setActiveElements', newActiveElements)
          let tri = document.createElement("div");
          tri.setAttribute("id", "triangle");
          document.getElementById(newActiveElements[0]).append(tri)

        }
      }
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
  },
  watch: {
    triggerHook() {
      this.scenes.forEach(scene => {
        scene.triggerHook(this.triggerHook)

      })
    },
    activeElements() {
      console.log('activeElements', this.activeElements)
    }
  }
}
</script>

<style >

  #essay {
    background-color: #dadada;
    padding-top: 32px;
    padding-right: 32px;
  }

  .vtl #essay  {
    padding-right: 0;
  }

  #essay h1, h2, h3, h4, h5, h6 {
    padding-left: 32px;
  }

  #essay p {
    padding-left: 20px;
    border-left: 12px solid white;
    font-size: 1em;
    line-height: 1.8;
    z-index: 1;
    cursor: default;
  }

  .vtl #essay p {
    padding-right: 32px;
    border-left: none;
    border-right: 1px solid  #dadada;;
    font-size: 1.4em;
    margin-bottom: 2.5em;
    padding-left: 32px;
  }

  #essay p.active-elem {
    border-left: 40px solid #1D5BC2;
    background-color: #ffffff;
    box-shadow:  4px 4px 4px 0 rgba(0,0,0,0.25)
  }

  .vtl #essay p.active-elem {
    border-right: 1px solid gray;
    border-left: none;
    width: calc(100% + 40px);
    padding-right: 60px
  }
  
  p.has-items:hover {
    cursor: pointer !important;
    background-color: #f7f7f7;;
  }

  .tagged.location,
  .tagged.building,
  .tagged.place,
  p.active-elem .inferred.location,
  p.active-elem .inferred.building,
  p.active-elem .inferred.place {
    background: #EBECBB;
    border-bottom: 2px solid #A9AC00;
    cursor: pointer;
    z-index: 10;
  }

  .tagged.person,
  .tagged.fictional_character,
  p.active-elem .inferred.person,
  p.active-elem .inferred.fictional_character {
    background: #FFDEF6;
    border-bottom: 2px solid #FF88DF;
    cursor: pointer;
    z-index: 10;
  }

  /* primary sources */
  .tagged.written_work {
    background: #E2EDFF;
    border-bottom: 2px solid #1D5BC2;
    cursor: pointer;
    z-index: 10;
  }

  .tagged.plant,
  p.active-elem .inferred.plant {
    background: #DFFFDF;
    border-bottom: 2px solid #187117;
    cursor: pointer;
    z-index: 10;
  }

  .tagged.entity,
  .tagged.event,
  p.active-elem .inferred.entity,
  p.active-elem .inferred.event {
    background: #FFDFDF;
    border-bottom: 2px solid #AF7171;
    cursor: pointer;
    z-index: 10;
  }

  #triangle {
    width: 0;
    height: 0;
    border-style: solid;
    border-width: 40px 40px 0 0;
    border-color: #666666 transparent transparent transparent;
    position: absolute;
    right: -40px;
  }

  section {
    position: relative
  }

</style>