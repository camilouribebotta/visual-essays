import Vue from 'vue'
import Vuetify from 'vuetify'
import VueScrollmagic from 'vue-scrollmagic'
import httpVueLoader from 'http-vue-loader'
import VueYoutube from 'vue-youtube'
import App from './App.vue'
import store from './store'
import 'leaflet'
// import 'scrollmagic/scrollmagic/uncompressed/plugins/debug.addIndicators.js'
import 'leaflet.control.opacity/dist/L.Control.Opacity.css'
import 'leaflet.control.opacity'
import '../assets/styles/main.css'
import { parseQueryString, prepItems, elemIdPath, itemsInElements, groupItems } from './utils'

// Default viewer components
import HorizontalViewer from './components/HorizontalViewer'
import VerticalViewer from './components/VerticalViewer'
import MapViewer from './components/MapViewer'
import ImageViewer from './components/ImageViewer'
import VideoPlayer from './components/VideoPlayer'
import EntityViewer from './components/EntityViewer'
import EntityInfobox from './components/EntityInfobox'
import EntityInfoboxDialog from './components/EntityInfoboxDialog'

const myMixin = {
  computed: {
    activeElement() { return store.getters.activeElement },
    activeElements() { return store.getters.activeElements },
    allItems() { return store.getters.items },
    groups() { return groupItems(itemsInElements(elemIdPath(this.activeElement), this.allItems)) },
    selectedItemID () { return store.getters.selectedItemID },
    // visualizerIsOpen() { return store.getters.visualizerIsOpen }
  }
}

let vm

let rtime
let timeout = false
const delta = 200

function setViewport() {
  const viewport = {
    height: Math.max(document.documentElement.clientHeight, window.innerHeight || 0),
    width: Math.max(document.documentElement.clientWidth, window.innerWidth || 0),
  }
  if (vm) {
    vm.$store.dispatch('setViewport', viewport )
  }
}

function resizeend() {
  if (new Date() - rtime < delta) {
    setTimeout(resizeend, delta)
  } else {
    timeout = false
    setViewport()
  }
}

const components = {
  horizontalViewer: HorizontalViewer,
  verticalViewer: VerticalViewer,
  gmap: MapViewer,
  entity: EntityViewer,
  gvideo: VideoPlayer,
  gimage: ImageViewer,
  entityInfobox: EntityInfobox,
  entityInfoboxDialog: EntityInfoboxDialog
}

function initApp() {
  console.log('visual-essays.init')
  console.log('window.data', window.data)

  window.data = []
  document.querySelectorAll('script[type="application/ld+json"]').forEach((scr) => {
    eval(scr.text)
  })
  console.log('window.data', window.data)

  window.data.filter(item => item.type === 'component').forEach(customComponent => {
    // console.log('customComponent', customComponent)
    components[customComponent.name] = httpVueLoader(customComponent.src)
  })

  Vue.config.productionTip = false
  Vue.config.devtools = true

  Vue.use(Vuetify)
  Vue.use(VueScrollmagic, {
    vertical: true,
    globalSceneOptions: {},
    loglevel: 2,
    refreshInterval: 100
  })
  Vue.use(VueYoutube)
  Vue.prototype.$L = L

  Object.entries(components).forEach(component => {
    component[1].mixins = [myMixin]
    // console.log(component[1])
    Vue.component(component[0], component[1])
  })

  vm = new Vue({
    template: '<App/>',
    store,
    render: h => h(App),
    vuetify: new Vuetify()
  })
  vm.$store.dispatch('setEssayHTML', undefined)
  vm.$store.dispatch('setContent', [])
  vm.$store.dispatch('setItems', [])

  vm.$store.dispatch('setItems', prepItems(window.data.filter(item => item.type !== 'component')))
  vm.$store.getters.items.forEach(item => console.log(`${item.id} ${item.label || item.title}`, item))

  vm.$store.dispatch('setEssayHTML', document.getElementById('essay').innerHTML)

  const qargs = parseQueryString()
  const config = vm.$store.getters.items.find(item => item.type === 'essay') || {}
  vm.$store.dispatch('setLayout', qargs.layout || config.layout)
  vm.$store.dispatch('setContext', qargs.context || config.context)
  vm.$store.dispatch('setDebug', (qargs.debug || config.debug || 'false') === 'true')
  console.log(`layout=${vm.$store.getters.layout} context=${vm.$store.getters.context} debug=${vm.$store.getters.debug}`)

  vm.$mount('#essay')

  setViewport()
  window.addEventListener('resize', () => {
    rtime = new Date()
    if (timeout === false) {
      timeout = true
      setTimeout(resizeend, delta)
    }
  })
}

//document.addEventListener('DOMContentLoaded', () => {
  let name
  let href = window.location.href
  const waitForContent = () => {
    // console.log('waitForContent')
    if (vm) {
      if (href !== window.location.href) {
        href = window.location.href
        console.log('remove vm')
        vm = vm.$destroy()
      }
    } else {
      const essayElem = document.getElementById('essay')
      // console.log('essay', name, essayElem, essayElem.innerText.length)
      if (essayElem && essayElem.dataset.name !== name && essayElem.innerText.length > 0) {
        initApp()
        vm.$store.getters.items.forEach((item) => {
          if (item.type === 'essay' && item.title) {
            essayElem.title = item.title
            console.log(essayElem.title)
          }
        })
        href = window.location.href
        name = essayElem.dataset.name
      }
    }
  }
  setInterval(() => waitForContent(), 250)
//}, false)
