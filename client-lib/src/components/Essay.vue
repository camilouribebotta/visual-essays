<template>
  <div ref="essay" id="essay" :class="layout[0] === 'v' ? 'vertical' : 'horizontal'" :style="style" v-html="html"/>
</template>

<script>
import { elemIdPath, itemsInElements, groupItems, eqSet } from '../utils'

export default {
  name: 'essay',
  data: () => ({
    paragraphs: {},
    scenes: [],
  }),
  computed: {
    html() { return this.$store.getters.essayHTML },
    debug() { return this.$store.getters.debug },
    viewportWidth() { return this.$store.getters.width },
    allItems() { return this.$store.getters.items },
    contentStartPos() { return this.$store.getters.contentStartPos },
    activeElements() { return this.$store.getters.activeElements },
    layout() { return this.$store.getters.layout },
    isMobile() { return this.$store.getters.isMobile },
    hoverItemID() { return this.$store.getters.hoverItemID },
    viewerIsOpen() { return this.$store.getters.viewerIsOpen },
    triggerHook() { return (this.contentStartPos + this.$store.getters.triggerOffset) / this.$store.getters.height },
    style() {
      return {
        padding: `${this.layout[0] === 'h' ? this.isMobile ? 12 : 32 : 0}px`
      }
    }
  },
  mounted() {
    this.$store.dispatch('setProgress', 0)
    groupItems(this.allItems, this.$store.getters.componentSelectors)
    this.$nextTick(() => this.init())
    if (window.location.hash) {
      this.scrollTo(window.location.hash.slice(1))
    }
  },
  methods: {
    init() {
      this.linkTaggedItems()
      // this.addFootnotesHover()

      // Setup ScrollMagic (https://scrollmagic.io/)
      let first
      let prior
      Array.from(document.body.querySelectorAll('p')).filter(elem => elem.id).forEach((para) => {
        if (!first) {
          first = para.id
        }
        para.title = elemIdPath(para.id).join(',')
        const itemsInPara = itemsInElements(elemIdPath(para.id), this.allItems)
        let scrollTop = para.offsetTop
        let elem = para
        while (elem.parentElement && elem.id !== 'essay') {
          elem = elem.parentElement
          scrollTop += elem.offsetTop
        }

        this.paragraphs[para.id] = {
          prior, 
          top: scrollTop,
          offset: para.offsetTop,
          items: itemsInPara
        }

        // console.log(`${para.id} ${itemsInPara.length}`)
        if (itemsInPara.length > 0) {
          para.classList.add('has-items')
          para.addEventListener('click', this.paragraphClickHandler)
        }

        // console.log(`${para.id} ${this.paragraphs[para.id].top} ${itemsInPara.length}`)
        prior = para.id
        const scene = this.$scrollmagic.scene({
          triggerElement: `#${para.id}`,
          triggerHook: this.triggerHook,
        })
        .on('enter', (e) => {
          // console.log(`enter=${para.id}`)
          this.setActiveElements(para.id)
        })
        .on('leave', (e) => {
          // console.log(`leave=${this.paragraphs[para.id].prior}`)
          this.setActiveElements(this.paragraphs[para.id].prior)
        })
        if (this.debug) {
          scene.addIndicators({indent: this.layout === 'vtl' ? this.viewportWidth/2 : 0})
        }
        this.$scrollmagic.addScene(scene)
        this.scenes.push(scene)
      })
      this.findContent()
      this.setActiveElements(first)
    },
    setActiveElements(elemId) {
      if (elemId) {
        const newActiveElements = elemIdPath(elemId)
        if (newActiveElements.length > 0 && !eqSet(new Set(this.activeElements), new Set(newActiveElements))) {
          if (document.getElementById('triangle')) {
            document.getElementById('triangle').remove();
          }
          this.$store.dispatch('setActiveElements', newActiveElements)

          if (this.layout === 'vtl') {
            //attach triangular shadow
            let tri = document.createElement("div");
            tri.setAttribute("id", "triangle");
            document.getElementById(newActiveElements[0]).append(tri)

            //move tab controls to active paragraph
            let ctrlTabs = document.querySelectorAll('[role="tablist"]');
            if (ctrlTabs && ctrlTabs.length > 0) {
              document.getElementById(newActiveElements[0]).append(ctrlTabs[0])
            }
            //this.setActiveElements(this.paragraphs[para.id].prior)

            //console.log(this.paragraphs.size)
            const contentParaIDs = Object.keys(this.paragraphs).filter(pid => pid.indexOf('section-') === 0)
            const idx = contentParaIDs.indexOf(newActiveElements[0])
            this.$store.dispatch('setProgress', Math.round(((idx+1)/contentParaIDs.length)*100))
          }
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
              offset: this.paragraphs[para.id].offset,
              top: this.paragraphs[para.id].top,
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
        document.body.querySelectorAll(`#essay h${i}`).forEach((heading) => {
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
            (item.tag !== 'entity' && item.tagged_in.has('essay'))) {
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
          const elemId = e.target.attributes['data-eid'].value
          this.$store.dispatch('setSelectedItemID', elemId)
        })
      })
    },
    paragraphClickHandler(e) {
      const paraId = e.target.tagName === 'P'
        ? e.target.id
        : e.target.parentElement.id
      console.log(`paragraphClickHandler para=${paraId}`, e)
      this.$store.dispatch('setSelectedParagraphID', paraId)
      if (this.paragraphs[paraId]) {
        let offset = -280
        let scrollable = document.getElementById('scrollableContent')
        if (scrollable) {
          offset = 120
        } else {
          scrollable = window
        }
        const scrollTo = this.paragraphs[paraId].top + offset
        console.log(`top=${this.paragraphs[paraId].top} offset=${offset} scrollto=${scrollTo}`)
        scrollable.scrollTo(0, scrollTo)
      }

    },
    setHoverItemID(e) {
      this.$store.dispatch('setHoverItemID', e.type === 'mouseover' ? e.target.dataset.eid : null)
    },
    itemClickHandler(e) {
      e.stopPropagation()
      const elemId = e.target.attributes['data-eid'].value
      this.$store.dispatch('setSelectedItemID', elemId)
    },
    addItemClickHandlers(elemId) {
      // console.log(`addItemClickHandlers: elemId=${elemId}`, document.getElementById(elemId))
      document.getElementById(elemId).querySelectorAll('.active-elem .inferred, .active-elem .tagged').forEach((entity) => {
        entity.addEventListener('click', this.itemClickHandler)
        entity.addEventListener('mouseover', this.setHoverItemID)
        entity.addEventListener('mouseout', this.setHoverItemID)
      })
    },
    removeItemClickHandlers(elemId) {
      // console.log(`removeItemClickHandlers: elemId=${elemId}`)
      const elem = document.getElementById(elemId)
      if (elem) {
        document.getElementById(elemId).querySelectorAll('.active-elem .inferred, .active-elem .tagged').forEach((entity) => {
          entity.removeEventListener('click', this.itemClickHandler)
          entity.removeEventListener('mouseover', this.setHoverItemID)
          entity.removeEventListener('mouseout', this.setHoverItemID)
        })
      }
    }
  },
  watch: {
    activeElement: {
      handler (active, prior) {
        console.log('Essay.activeElement', active)
        if (prior) {
          this.removeItemClickHandlers(prior)
          document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
        }
        if (active) {
          if (this.viewerIsOpen) {
            document.getElementById(active).classList.add('active-elem')
          }
          this.addItemClickHandlers(active)
          const tabsBarElem = document.querySelector('.v-tabs-bar')
          if (tabsBarElem) {
            // console.log(`tabsBarElem: offset=${this.paragraphs[active].offset} top=${this.paragraphs[active].top}`)
            tabsBarElem.style.top = `${this.paragraphs[active].offset}px`
          }
        }
      },
      immediate: true
    },
    hoverItemID: {
      handler: function (itemID, prior) {
        // console.log(`Essay.hoverItemID: value=${itemID} prior=${prior}`)
        if (itemID) {
          document.querySelectorAll(`.active-elem [data-eid="${itemID}"]`).forEach(elem => elem.classList.add('entity-highlight'))
        }
        if (prior) {
          document.querySelectorAll(`.active-elem [data-eid="${prior}"]`).forEach(elem => elem.classList.remove('entity-highlight'))
        }
      },
      immediate: true
    },
    triggerHook: {
      handler: function () {
        this.scenes.forEach(scene => {
          scene.triggerHook(this.triggerHook)
        })
      },
      immediate: true
    }
  }
}
</script>

<style>

 #essay.vertical h1, .vtl #essay h2, .vtl #essay h3, .vtl #essay h4, .vtl #essay h5, .vtl #essay h6 {
    padding-left: 32px;
  }

  #essay.vertical p {
    padding: 6px 6px 0 6px;
    /* border-left: 12px solid white; */
    font-size: 1em;
    line-height: 1.8;
    z-index: 1;
    cursor: default;
  }

  .vtl #essay p {
    padding-right: 32px;
    border-left: none;
    font-size: 1.4em;
    /* margin-bottom: 2.5em; */
    padding-left: 32px;
  }

  #essay p.active-elem {
    /* border-left: 40px solid #1D5BC2; */
    background-color: #ffffff;
    box-shadow:  4px 4px 4px 0 rgba(0,0,0,0.25)
  }

  .vtl #essay p.active-elem {
    border-left: none;
    width: calc(100% + 20px);
    padding-right: 52px
  }
  
  p.has-items:hover {
    cursor: pointer !important;
    background-color: #f7f7f7;;
  }

  .tagged.location,
  p.active-elem .inferred.location,
  .tagged.building,
  p.active-elem .inferred.building,
  .tagged.place,
  p.active-elem .inferred.place,
  .tagged.person,
  p.active-elem .inferred.person,
  .tagged.fictional_character,
  p.active-elem .inferred.fictional_character,
  .tagged.written_work,
  p.active-elem .inferred.written_work,
  .tagged.plant,
  p.active-elem .inferred.plant,
  .tagged.entity,
  p.active-elem .inferred.entity,
  .tagged.event,
  p.active-elem .inferred.event {
    border-bottom: 2px solid #A9AC00;
    cursor: pointer;
    z-index: 10;
  }

  .entity-highlight,
  .tagged.location:hover,
  p.active-elem .inferred.location:hover,
  .tagged.building:hover,
  p.active-elem .inferred.building:hover,
  .tagged.place:hover,
  p.active-elem .inferred.place:hover,
  .tagged.person:hover,
  p.active-elem .inferred.person:hover,
  .tagged.fictional_character:hover,
  p.active-elem .inferred.fictional_character:hover,
  .tagged.written_work:hover,
  p.active-elem .inferred.written_work:hover,
  .tagged.plant:hover,
  p.active-elem .inferred.plant:hover,
  .tagged.entity:hover,
  p.active-elem .inferred.entity:hover,
  .tagged.event:hover,
  p.active-elem .inferred.event:hover {
    background: #EBECBB !important;
  }

  /*
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

  .tagged.written_work,
  p.active-elem .inferred.written_work {
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
  */

  #triangle {
    width: 0;
    height: 0;
    border-style: solid;
    border-width: 20px 20px 0 0;
    border-color: #666666 transparent transparent transparent;
    position: absolute;
    right: -20px;
    /* bottom: -20px; */
  }

  section {
    position: relative
  }

</style>