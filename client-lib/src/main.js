import Vue from 'vue'
import Vuetify from 'vuetify'
import VueScrollmagic from 'vue-scrollmagic'
import httpVueLoader from 'http-vue-loader'
import VueYoutube from 'vue-youtube'
import App from './App.vue'
import store from './store'
import 'vuetify/dist/vuetify.min.css'
import Lingallery from '../assets/js/lingallery.umd.min.js'
import marked from 'marked'

import 'leaflet'
import 'leaflet-polylinedecorator'

// import 'scrollmagic/scrollmagic/uncompressed/plugins/debug.addIndicators.js'
import 'leaflet.control.opacity/dist/L.Control.Opacity.css'
import 'leaflet.control.opacity'
import '../assets/styles/main.css'
import { parseQueryString, prepItems, elemIdPath, itemsInElements, groupItems } from './utils'

import '../assets/js/leaflet-fa-markers.js'
import '../assets/js/fontawesome-pro.min.js'

import 'leaflet.control.opacity'

// Default viewer components
import HorizontalViewer from './components/HorizontalViewer'
import VerticalViewer from './components/VerticalViewer'
import MapViewer from './components/MapViewer'
import ImageViewer from './components/ImageViewer'
import VideoPlayer from './components/VideoPlayer'
import EntityViewer from './components/EntityViewer'
import EntityInfobox from './components/EntityInfobox'
import EntityInfoboxDialog from './components/EntityInfoboxDialog'

const VERSION = '0.5.37'

console.log(`visual-essays js lib ${VERSION}`)

Vue.component('lingallery', Lingallery)

const myMixin = {
  computed: {
    activeElement() { return store.getters.activeElement },
    activeElements() { return store.getters.activeElements },
    allItems() { return store.getters.items },
    groups() { return groupItems(itemsInElements(elemIdPath(this.activeElement), this.allItems)) },
    selectedItemID () { return store.getters.selectedItemID }
    // visualizerIsOpen() { return store.getters.visualizerIsOpen }
  }
}

const breakpoint = 480
const screenWidth = Math.max(document.documentElement.clientWidth, window.innerWidth || 0)
const isMobile = screenWidth <= breakpoint

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
    vm.$store.dispatch('setViewport', viewport)
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

const initialStateCopy = JSON.parse(JSON.stringify(store.state))

function resetState () {
  store.replaceState(JSON.parse(JSON.stringify(initialStateCopy)))
}

function initApp() {
  console.log('visual-essays.init', window.app)

  resetState()

  window.data = []
  document.querySelectorAll('script[type="application/ld+json"]').forEach((scr) => {
    eval(scr.text)
  })

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
  Vue.prototype.$marked = marked

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
  console.log(`geoJsonCache cache_size=${Object.keys(vm.$store.getters.geoJsonCache).length}`)

  vm.$store.dispatch('setEssayHTML', undefined)

  vm.$store.dispatch('setContent', [])
  vm.$store.dispatch('setItems', [])

  vm.$store.dispatch('setItems', prepItems(window.data.filter(item => item.type !== 'component')))
  vm.$store.getters.items.forEach(item => console.log(`${item.id} ${item.label || item.title}`, item))

  vm.$store.dispatch('setEssayHTML', document.getElementById('essay').innerHTML)

  const qargs = parseQueryString()
  const essayConfig = vm.$store.getters.items.find(item => item.type === 'essay') || {}
  vm.$store.dispatch('setLayout', isMobile ? 'hc' : (qargs.layout || essayConfig.layout || 'hc' ))
  vm.$store.dispatch('setShowBanner', window.app === undefined && !(qargs.nobanner === 'true' || qargs.nobanner === ''))
  vm.$store.dispatch('setContext', qargs.context || essayConfig.context)
  vm.$store.dispatch('setDebug', (qargs.debug || essayConfig.debug || 'false') === 'true')
  // vm.$store.dispatch('setTrigger', window.triggerPosition || vm.$store.getters.trigger)
  console.log(`layout=${vm.$store.getters.layout} showBanner=${vm.$store.getters.showBanner} context=${vm.$store.getters.context} debug=${vm.$store.getters.debug}`)

  if (window.app) {
    window.app.essayConfig = essayConfig
    window.app.libVersion = VERSION
  } else {
    vm.$store.dispatch('setEssayConfig', essayConfig)
  }

  vm.$mount('#essay')
  if (window.app) {
    window.app.isLoaded = true
  }

  setViewport()
  window.addEventListener('resize', () => {
    rtime = new Date()
    if (timeout === false) {
      timeout = true
      setTimeout(resizeend, delta)
    }
  })
}

let current = undefined
const waitForContent = () => {
  // console.log(`waitForContent: current=${current} window._essay=${window._essay}`)
  const essayElem = document.getElementById('essay')
  if (!window._essay && essayElem && essayElem.innerText.length > 0) {
    window._essay = essayElem.dataset.name
  }
  if (current != window._essay) {
    current = window._essay
    if (vm) {
      vm = vm.$destroy()
    }
    initApp()
  }
}
setInterval(() => waitForContent(), 250)