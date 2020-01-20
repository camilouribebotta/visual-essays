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
      scrollingElement: null,
      offsets: {
        scrollTo: 10,
        activeElem: 340
      },
      isOpen: false,
      mouseOver: null
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
      addSpacer() {
        // Adds a spacer element that expands and contracts to match the size of the BottomSheet so
        // that content at the end of the article is still reachable by scrolling
        this.spacer = document.createElement('div')
        this.spacer.style.height = '0'
        this.spacer.id = 'essay-spacer'
        document.getElementById('essay').appendChild(this.spacer)
      },
      makeHeadingsClickable() {
        for (let i = 1; i < 9; i++) {
          document.body.querySelectorAll(`h${i}`).forEach((heading) => {
            heading.addEventListener('click', (e) => this.toggle(e.target.parentElement.id))
          })
        }
      },
      makeSectionsClickable() {
        for (let i = 1; i < 9; i++) {
          document.body.querySelectorAll(`h${i}`).forEach((heading) => {
            const section = heading.parentElement
            section.addEventListener('click', (e) => this.toggle(e.target.parentElement.id))
          })
        }
      },
      makeParagraphsClickable() {
        this.content.forEach((elem) => {
          if (elem.paragraphs) {
            elem.paragraphs.forEach((para) => {
              document.getElementById(para.id).addEventListener('click', (e) => this.toggle(e.target.id))
            })
          }
        })
      },
      toggle(elemId) {
        if (elemId) {
          if (this.isOpen) {
            this.close()
          } else {
            this.spacer.style.height = `${this.viewport.height/2}px`
            this.positionElementInViewport(elemId)
            this.isOpen = true
          }
        }
      },
      close() {
        this.spacer.style.height = '0px'
        const currentElem = document.getElementById(this.activeElement.id)
        currentElem.classList.remove('active-elem')
        /*
        currentElem.querySelectorAll('.entity.inferred').forEach((entity) => {
          entity.removeEventListener('click', this.clickHandler)
        })
        */
        this.isOpen = false
      },
      positionElementInViewport(elemId) {
        for (let i = 0; i < this.content.length; i++) {
          const elem = this.content[i]
          if (elemId === elem.id) {
            const elemHeight = elem.bottom - elem.top
            const viewPaneHeight = this.viewport.height/2
            const topPadding = viewPaneHeight - elemHeight
            const scrollTo = viewPaneHeight > elemHeight
              ? elem.top - topPadding + this.offsets.scrollTo
              : elem.top - 10
            // console.log(`positionElementInViewport: element=${elem.id} viewPaneHeight=${viewPaneHeight} elemHeight=${elemHeight} elemTop=${elem.top} topPadding=${topPadding} scrollTo=${scrollTo}`)
            this.scrollingElement.scrollTo(0, scrollTo)
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
        pos += this.offsets.activeElem
        const currentActiveElemIds = new Set()
        this.$store.getters.activeElements.forEach(e => currentActiveElemIds.add(e.id))
        const updatedActiveElemIds = new Set()
        const updated = []
        this.$store.getters.content.forEach((elem) => {
          if (pos >= elem.top && pos <= elem.bottom) {
            if (elem.paragraphs) {
              elem.paragraphs.forEach((para) => {
                if (pos >= para.top && pos <= para.bottom) {
                  if (!updatedActiveElemIds.has(para.id)) {
                    updated.push(para)
                    updatedActiveElemIds.add(para.id)
                  }
                }
              })
            //} else {
            //  if (!updatedActiveElemIds.has(elem.id)) {
            //    updated.push(elem)
            //    updatedActiveElemIds.add(elem.id)
            //  }
            }
            if (!updatedActiveElemIds.has(elem.id)) {
              updated.push(elem)
              updatedActiveElemIds.add(elem.id)
            }
          }
        })
        // console.log(currentActiveElemIds, updatedActiveElemIds, this.setsEqual(currentActiveElemIds, updatedActiveElemIds))
        if (!this.setsEqual(currentActiveElemIds, updatedActiveElemIds)) {
          // updated.sort().reverse()
          if (updated.length > 0) {
            this.$store.dispatch('setActiveElements', updated)        
          }
        }
      },
      handleScroll: throttle(function (event) {
        this.scrollingElement = event.target.scrollingElement ? event.target.scrollingElement : event.target
        event.preventDefault()
        event.stopPropagation()
        const pos = this.isOpen && this.scrollingElement.scrollTop > 0
          ? (this.scrollingElement.scrollTop + this.viewport.height/2) - 60
          : this.scrollingElement.scrollTop + 20
        this.setActiveElements(this.scrollingElement.scrollTop)     
      }, 300),
      handleMouseMove: throttle(function (event) {
        const where = this.isOpen ? event.clientY <= this.viewport.height/2 ? 'document' : 'viewer' : 'essay'
        if (where !== this.mouseOver) {
          this.mouseOver = where
          // console.log(`mouseOver=${this.mouseOver}`)
        }
      }, 100),
      clickHandler(e) {
        // console.log(e)
        // console.log(this.$refs)
      }
    },
    watch: {
      content: {
          handler: function (content) {
          if (content) {
            window.scrollTo(0, 0)
            this.setActiveElements(content[0].top)
            this.makeHeadingsClickable()
            this.makeParagraphsClickable()
            //this.makeSectionsClickable()
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
        // console.log('activeElements:', current)
      },
      activeElement(current, prior) {
        // console.log(`activeElement: current=${current ? current.id : null} prior=${prior ? prior.id : null}`)
        if (this.isOpen) {
          if (prior) {
            const priorElem = document.getElementById(prior.id)
            priorElem.classList.remove('active-elem')
            /*
            priorElem.querySelectorAll('.entity.inferred').forEach((entity) => {
              entity.removeEventListener('click', this.clickHandler)
            })
            */
          }
          if (current) {
            const currentElem = document.getElementById(current.id)
            currentElem.classList.add('active-elem')
            /*
            currentElem.querySelectorAll('.entity.inferred').forEach((entity) => {
              entity.addEventListener('click', this.clickHandler)
            })
            */
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
    border-left: 4px solid blue;
  }

  p.active-elem .inferred {
    border-bottom: 2px solid red;
    cursor: pointer;
  }

  .v-bottom-sheet.v-dialog {
    height: 50%;
    background: white;
  }

</style>

