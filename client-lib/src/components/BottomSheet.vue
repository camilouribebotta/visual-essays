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
  import Viewer from './Viewer'
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
      contentContainer: undefined,
      scrollingElement: undefined,
      isOpen: false,
      mouseOver: null,
      selectedElem: undefined,
      ignoreScrollEvents: false
    }),
    computed: {
      content() { return this.$store.getters.content },
      activeElement() { return this.$store.getters.activeElement },
      viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
      topMargin() { return this.$store.getters.topMargin }
    },
    created() {
      this.isOpen = this.show
    },
    mounted() {
      // add scroll listener to update visible sections list in store
      this.contentContainer = document.getElementById('scrollableContent')
      if (!this.contentContainer) {
        this.contentContainer = window.document
      }
      this.contentContainer.addEventListener('scroll', this.handleScroll)
      this.addSpacer()
    },
    beforeDestroy() {
      this.close()
      let element = document.getElementById('bottom-sheet')
      element.parentNode.removeChild(element)
      document.querySelectorAll('.layout').forEach(elem => elem.height = `1000px`)
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
          this.$store.dispatch('setActiveElement', this.selectedElem)
        }
      },
      close() {
        this.spacer.style.height = '0px'
        // removeClickHandlers
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
              let scrollTo = elem.top - topPadding + 10 > 0
                  ? elem.top - topPadding + 10
                  : elem.top - 10
              scrollTo += this.topMargin
              // console.log(`elem=${elem.id} elemTop=${elem.top} elemHeight=${elemHeight} viewPaneHeight=${viewPaneHeight} topPadding=${topPadding} scrollTo=${scrollTo}`)
              this.ignoreScrollEvents = true
              this.scrollingElement.scrollTo(0, scrollTo)
              setTimeout(() => { this.ignoreScrollEvents = false }, 1000)
            }
            break
          }
        }
      },
      handleScroll: throttle(function (event) {
        event.preventDefault()
        event.stopPropagation()
        if (!this.ignoreScrollEvents) {
          this.scrollingElement = event.target.scrollingElement ? event.target.scrollingElement : event.target
          if (this.isOpen) {
            const pos = this.scrollingElement.scrollTop - this.topMargin
            const client = this.scrollingElement.clientHeight
            const textWindowHeight = client/2 - 40
            const relPos = pos + pos/textWindowHeight * textWindowHeight
            const refPos = pos > textWindowHeight ? textWindowHeight + pos : relPos
            const activeElem = this.nearestPara(refPos)
            document.querySelectorAll('.active-elem').forEach(elem => elem.classList.remove('active-elem'))
            document.getElementById(activeElem.id).classList.add('active-elem')
            this.$store.dispatch('setActiveElement', activeElem)
          }
          // console.log(`scrollTop=${this.scrollingElement.scrollTop} scrollHeight=${this.scrollingElement.scrollHeight} clientTop=${this.scrollingElement.clientTop} clientHeight=${this.scrollingElement.clientHeight} topMargin=${this.topMargin}`)
        }
      }, 200)
    },
    watch: {
      content(content) {
        if (content) {
          // window.scrollTo(0, 0)
          this.makeParagraphsClickable()
        }
      },
      viewport(value, prior) {
        this.spacer.style.height = this.isOpen ? `${this.viewport.height/2}px` : '0px'
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

