<template>
  <div id="bottom-sheet" tabindex="-1" class="v-dialog__content v-dialog__content--active">
    <transition name="bottom-sheet-transition">
      <div class="v-dialog v-dialog--active v-dialog--scrollable v-bottom-sheet" v-if="isOpen">
        <v-card style="padding:0; margin:0;">
          <!-- <v-card-actions>
            <v-btn @click="close" text>Close</v-btn>
          </v-card-actions> -->
          <v-card-text style="padding:0; margin:0;" class="text-center">
            <div style="height: 100%;">
              <viewer/>
            </div>
          </v-card-text>
        </v-card>     
      </div>
    </transition>
  </div>
</template>

<script>
  import Viewer from './Viewer1'
  import { throttle } from 'lodash'

  export default {
    name: 'BottomSheet',
    components: {
      Viewer
    },
    props: {
      show: { type: Boolean, default: false }
    },
    data: () => ({
      scrollingElement: undefined,
      offsets: {
        scrollTo: 10,
        activeElem: 0
      },
      isOpen: false,
      mouseOver: null,
      selectedElem: undefined
    }),
    computed: {
      content() { return this.$store.getters.content },
      activeElements() { return this.$store.getters.activeElements },
      activeElement() { return this.activeElements.length > 0 ? this.activeElements[0] : null },
      viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} }
    },
    created() {
      this.isOpen = this.show
    },
    mounted() {
      // add scroll listener to update visible sections list in store
      let contentContainer = document.getElementById('scrollableContent')
      if (contentContainer) {
        this.offsets.scrollTo = 290
        this.offsets.activeElem = 220
      } else {
        contentContainer = window.document
      }
      contentContainer.addEventListener('scroll', this.handleScroll)
      // window.addEventListener('mousemove', this.handleMouseMove)
      this.addSpacer()
    },
    methods: {
      nearestPara(pos) {
        let nearest = undefined
        this.content
          .filter(elem => elem.type === 'paragraph')
          .forEach(para => {
            if (!nearest || pos >= para.top) { nearest = para }
          })
        // console.log(`nearest pos=${pos} elem=${nearest.id}`)
        return nearest
      },
      addSpacer() {
        // Adds a spacer element that expands and contracts to match the size of the BottomSheet so
        // that content at the end of the article is still reachable by scrolling
        this.spacer = document.createElement('div')
        this.spacer.style.height = '0'
        this.spacer.id = 'essay-spacer'
        document.getElementById('essay').appendChild(this.spacer)
      },
      makeParagraphsClickable() {
        this.content.forEach((elem) => {
          if (elem.type === 'paragraph') {
            document.getElementById(elem.id).addEventListener('click', (e) => this.toggle(e.layerY))
          }
        })
      },
      toggle(pos) {
        this.selectedElem = this.nearestPara(pos)
        console.log(`BottomSheet.toggle: pos=${pos} isOpen=${this.isOpen} elemId=${this.selectedElem.id}`)
        if (this.isOpen) {
          this.close()
        } else {
          this.spacer.style.height = `${this.viewport.height/2}px`
          this.isOpen = true
          this.positionElementInViewport(this.selectedElem.id)
          document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
          document.getElementById(this.selectedElem.id).classList.add('active-elem')
        }
      },
      close() {
        this.spacer.style.height = '0px'
        document.querySelectorAll('p.active-elem .inferred, p.active-elem .tagged').forEach((entity) => {
          entity.removeEventListener('click', this.clickHandler)
        })
        document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
        this.isOpen = false
      },
      positionElementInViewport(elemId) {
        // console.log(`positionElementInViewport: elem=${elemId} scrollingElement=${this.scrollingElement !== undefined}`)
        for (let i = 0; i < this.content.length; i++) {
          const elem = this.content[i]
          if (elemId === elem.id) {
            const elemHeight = elem.bottom - elem.top
            const viewPaneHeight = this.viewport.height/2
            const topPadding = viewPaneHeight - elemHeight
            if (this.scrollingElement) {
              const scrollTo = elem.top - topPadding + 10 > 0
                  ? elem.top - topPadding + 10
                  : elem.top - 10
            // console.log(`elem=${elem.id} elemTop=${elem.top} elemHeight=${elemHeight} viewPaneHeight=${viewPaneHeight} topPadding=${topPadding} scrollTo=${scrollTo}`)
              this.scrollingElement.scrollTo(0, scrollTo)
              this.setActiveElements(scrollTo + viewPaneHeight)
            }
            break
          }
        }
      },
      setsEqual(as, bs) {
        if (as.size !== bs.size) return false
          for (var a of as) if (!bs.has(a)) return false
          return true
      },
      setActiveElements(pos) {
        const currentActiveElemIds = new Set(this.$store.getters.activeElements.map(e => e.id))
        const updatedActiveElemIds = new Set()
        const updated = []

        this.$store.getters.content.forEach((elem) => {
          if (elem.type !== 'paragraph') {
            if (pos >= elem.top && pos <= elem.bottom) {
              if (elem.paragraphs) {
                let ap = elem.paragraphs[0]
                for (let i = 0; i < elem.paragraphs.length; i++) {
                  const para = elem.paragraphs[i]
                  if (pos >= para.top) {
                    ap = para
                  }
                  if (pos < para.bottom) {
                    break
                  }
                }
                if (!updatedActiveElemIds.has(ap.id)) {
                  updated.push(ap)
                  updatedActiveElemIds.add(ap.id)
                }
              }
              if (!updatedActiveElemIds.has(elem.id)) {
                updated.push(elem)
                updatedActiveElemIds.add(elem.id)
              }
            }
          }
        })
        if (!this.setsEqual(currentActiveElemIds, updatedActiveElemIds)) {
          if (updated.length > 0) {
            // console.log('setActiveElements', currentActiveElemIds, updatedActiveElemIds, this.setsEqual(currentActiveElemIds, updatedActiveElemIds))
            this.$store.dispatch('setActiveElements', updated)        
          }
        }
      },
      handleScroll: throttle(function (event) {
        if (!this.ignoreScrollEvents) {
          this.scrollingElement = event.target.scrollingElement ? event.target.scrollingElement : event.target
          // console.log('handleScroll', this.scrollingElement.scrollTop)
          event.preventDefault()
          event.stopPropagation()
          const viewPaneSize = this.isOpen ? this.viewport.height/2 : this.viewport.height
          let pos = this.isOpen
            ? (this.scrollingElement.scrollTop + this.viewport.height/2) - 10
            : this.scrollingElement.scrollTop
          if (!this.selectedElem) {
            this.setActiveElements(pos)
          }
          this.selectedElem = undefined
        }
      }, 300),
      handleMouseMove: throttle(function (event) {
        const where = this.isOpen ? event.clientY <= this.viewport.height/2 ? 'document' : 'viewer' : 'essay'
        if (where !== this.mouseOver) {
          this.mouseOver = where
          // console.log(`mouseOver=${this.mouseOver}`)
        }
      }, 100)
    },
    watch: {
      content: {
          handler: function (content) {
          if (content) {
            window.scrollTo(0, 0)
            this.setActiveElements(content[0].top)
            this.makeParagraphsClickable()
          }
        },
        immediate: false
      },
      viewport: {
        handler: function (value, prior) {
          // adjust spacer size based using new viewport height
          this.spacer.style.height = this.isOpen ? `${this.viewport.height/2}px` : '0px'
        },
        immediate: false
      },
      activeElements(current, prior) {
        // console.log('activeElements:', current.map(e => e.id).join(', '))
      },
      activeElement(current, prior) {
        // console.log(`activeElement: current=${current ? current.id : null} prior=${prior ? prior.id : null} isOpen=${this.isOpen} selected=${this.selectedElem !== undefined}`)
        if (this.isOpen && !this.selectedElem) {
          document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
          if (current) {
            document.getElementById(current.id).classList.add('active-elem')
          }
        }
      }
    }
  }
</script>

<style>

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

  .v-bottom-sheet.v-dialog {
    height: 50%;
    background: white;
  }

</style>

