<template>
  <div ref="essay" id="essay" v-html="html"/>    
</template>

<script>
import { addActivator } from './Activator'
import { elemIdPath, itemsInElements, groupItems } from '../utils'

export default {
  name: 'essay',
  data: () => ({
    paragraphs: {},
    spacer: undefined,
    activators: undefined
  }),
  computed: {
    html() { return this.$store.getters.essayHTML },
    debug() { return this.$store.getters.debug },
    visualizerIsOpen() { return this.$store.getters.visualizerIsOpen },
    activeElement() { return this.$store.getters.activeElement },
    layout() { return this.$store.getters.layout },
    viewportHeight() { return this.$store.getters.height },
    viewportWidth() { return this.$store.getters.width },
    allItems() { return this.$store.getters.items }
  },
  mounted() {
    groupItems(this.allItems)
    this.addSpacer()
    this.$nextTick(() => this.init())
    if (window.location.hash) {
      this.scrollTo(window.location.hash.slice(1))
    }
  },
  methods: {
    offset(el) {
      var rect = el.getBoundingClientRect(),
      scrollLeft = window.pageXOffset || document.documentElement.scrollLeft,
      scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      return { top: rect.top + scrollTop, left: rect.left + scrollLeft }
    },
    addActivators() {
      // console.log('addActivators')
      const essay = this.$refs.essay
      Array.from(document.body.querySelectorAll('p')).filter(elem => elem.id).forEach((para) => {
        const paraData = this.paragraphs[para.id]
        // console.log(`${para.id} items=${paraData.items.map(item => item.id).join(',')}`)
        if (paraData.items.length > 0) {
          addActivator(essay, para.id, paraData.top, paraData.items.map(item => item.id).join(','), this.clickHandler)
        }
      })
    },
    clickHandler(e) {
      const selectedParaId = e.target.parentElement.attributes['data-id'].value
      this.toggleVisualizer(selectedParaId)
    },
    init() {
      this.findContent()
      this.addFootnotesHover()
    
      console.dir(this.$refs.essay)
      // const offsets = this.offset(this.$refs.essay)
      // console.log(offsets)

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
        //if (this.layout === 'horizontal') {
        //  para.addEventListener('click', (e) => { this.toggleVisualizer(e.toElement.id) })
        //}
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
      this.addActivators()
    },
    eqSet(as, bs) {
      if (as.size !== bs.size) return false;
      for (var a of as) if (!bs.has(a)) return false;
      return true;
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
    toggleVisualizer(elemId) {
      // Toggles display of visualizer pane
      // e.preventDefault()
      // e.stopPropagation()
      if (this.paragraphs[elemId]) {
        console.log('toggleVisualizer')
        this.$store.dispatch('setVisualizerIsOpen', true)
        document.querySelectorAll('.activator').forEach(activator => activator.style.display = 'none')
        let offset = 100
        let scrollable = document.getElementById('scrollableContent')
        if (scrollable) {
          offset = -80
        } else {
          scrollable = window
        }
        const scrollTo = this.paragraphs[elemId].top - offset
        // console.log(`scrollTo: elem=${elemId} top=${scrollTo}`)
        this.spacer.style.height = `${this.viewportHeight*0.7}px`
        scrollable.scrollTo(0, scrollTo )
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
      // console.log(`activeElement=${active}`)
      console.log(active, groupItems(itemsInElements(elemIdPath(active), this.allItems)))
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
        this.spacer.style.height = `${this.viewportHeight*0.7}px`
        document.getElementById(this.activeElement).classList.add('active-elem')
      }
    },
    viewportHeight() {
      if (this.layout === 'vertical') {
        this.spacer.style.height = `${this.viewportHeight/2}px`
      }
    },
    viewportWidth() {    
      Array.from(document.body.querySelectorAll('p')).filter(elem => elem.id).forEach((para) => {
        this.paragraphs[para.id].top = para.offsetTop
      })
      document.querySelectorAll('.activator').forEach((activator) => {
        const paraId = activator.attributes['data-id'].value
        activator.style.top = `${this.paragraphs[paraId].top}px`
      })
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

  span.activator i {
    color: #eee;
    opacity: 0.4;
  }

  span.activator i:hover {
    color: blue;
    opacity: 1;
  }

</style>