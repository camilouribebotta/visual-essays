<template>
  <div id="essay" v-html="html"/>    
</template>

<script>
import ScrollMagic from 'scrollmagic'

export default {
  name: 'essay',
  data: () => ({
    controller: new ScrollMagic.Controller(),
    paragraphs: {},
    spacer: undefined
  }),
  computed: {
    html() { return this.$store.getters.essayHTML },
    debug() { return this.$store.getters.debug },
    visualizerIsOpen() { return this.$store.getters.visualizerIsOpen },
    activeElement() { return this.$store.getters.activeElement },
    layout() { return this.$store.getters.layout },
    viewportHeight() { return this.$store.getters.height }
  },
  mounted() {
    this.addSpacer()
    this.$nextTick(() => this.init())
    if (window.location.hash) {
      this.scrollTo(window.location.hash.slice(1))
    }
    this.addFootnotesHover()

    // Setup ScrollMagic (https://scrollmagic.io/)
    let prior
    Array.from(document.body.querySelectorAll('p')).filter(elem => elem.id).forEach((para) => {
      para.title = para.id
      this.paragraphs[para.id] = { prior, top: para.offsetTop }
      prior = para.id
      if (this.layout === 'horizontal') {
        para.addEventListener('click', (e) => { this.toggleVisualizer(e) })
      }
      const scene = new ScrollMagic.Scene({
        triggerElement: `#${para.id}`,
        triggerHook: 0.25
      })
      .on('enter', (e) => { this.setActiveElements(para.id) })
      .on('leave', (e) => {
        if (e.scrollDirection === 'REVERSE' || e.scrollDirection === 'PAUSED') {
          this.setActiveElements(this.paragraphs[para.id].prior)
        }
      })
      if (this.debug) {
        scene.addIndicators()
      }
      scene.addTo(this.controller)
    })
  },
  methods: {
    init() {
      this.aggregateItemMappings()
      this.findContent()
    },
    eqSet(as, bs) {
      if (as.size !== bs.size) return false;
      for (var a of as) if (!bs.has(a)) return false;
      return true;
    },
    setActiveElements(elemId) {
      const activeElements = []
      let elem = document.getElementById(elemId)
      while(elem) {
        activeElements.push(elem.id)
        if (elem.id === 'essay') {
          break
        }
        elem = elem.parentElement
      }
      // console.log(activeElements, this.activeElements, this.eqSet(new Set(activeElements), new Set(this.activeElements)))
      this.$store.dispatch('setActiveElements', activeElements)
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
      console.log(content)
      this.$store.dispatch('setContent', content)
    },
    aggregateItemMappings() {
      this.$store.getters.items.forEach((item) => {
        item.part_of = new Set()
        if (item.tagged_in) {
          item.tagged_in.forEach((elemId) => { item.part_of.add(elemId) }) 
        }        
        if (item.found_in) {
          item.found_in.forEach((elemId) => { item.part_of.add(elemId) }) 
        }
      })
    },
    itemsPartOf(elemId) {
      const items = []
      this.$store.getters.items.forEach((item) => {
        if (item.part_of.has(elemId) || (item.type !== 'entity' && item.part_of.has('essay'))) {
          items.push(item)
        }
      })
      return items
    },
    toggleVisualizer(e) {
      // Toggles display of visualizer pane
      console.log('toggleVisualizer')
      this.$store.dispatch('setVisualizerIsOpen', !this.visualizerIsOpen)
      if (this.visualizerIsOpen) {
        let offset = 100
        let scrollable = document.getElementById('scrollableContent')
        if (scrollable) {
          offset = -80
        } else {
          scrollable = window
        }
        const scrollTo = this.paragraphs[e.toElement.id].top - offset
        // console.log(`scrollTo: elem=${e.toElement.id} top=${scrollTo}`)
        this.spacer.style.height = `${this.viewportHeight/2}px`
        scrollable.scrollTo(0, scrollTo )
      } else {
        this.spacer.style.height = 0
      }
    },
    addSpacer() {
      // Adds a spacer element that expands and contracts to match the size of the visualizer so
      // that content at the end of the article is still reachable by scrolling
      this.spacer = document.createElement('div')
      this.spacer.id = 'essay-spacer'
      this.spacer.style.height = 0
      document.getElementById('essay').appendChild(this.spacer)
    },
    scrollTo(elemid) {
      // console.log(`scrollTo=${elemid}`)
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
    }
  },
  watch: {
    activeElement(active, prior) {
      console.log(`activeElement=${active}`)
      if (this.visualizerIsOpen) {
        if (prior) {
          document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
        }
        if (active) {
          document.getElementById(active).classList.add('active-elem')
        }
      }
    },
    visualizerIsOpen(isOpen) {
      if (!isOpen) {
        this.spacer.style.height = 0
        document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
      } else if (this.activeElement) {
        this.spacer.style.height = `${this.viewportHeight/2}px`
        document.getElementById(this.activeElement).classList.add('active-elem')
      }
    },
    viewportHeight() {
      if (this.layout === 'vertical') {
        this.spacer.style.height = `${this.viewportHeight/2}px`
      }
    }
  }
}
</script>

<style>

  #essay {
    height: 100%;
  }

  h1, h2, h3, h4, h5, h6 {
    margin-top: 24px;
    margin-bottom: 12px;
  }

  section p {
    padding-left: 12px;
    border-left: 4px solid transparent;
  }

  p.active-elem {
    border-left: 4px solid #8FBC8F;
  }

  p.active-elem .inferred, p.active-elem .tagged {
    border-bottom: 2px solid #8FBC8F;
    cursor: pointer;
  }

</style>