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

import mirador from '../assets/js/mirador.min.js'

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
import Essay from './components/Essay'
import EntityInfoboxDialog from './components/EntityInfoboxDialog'

import MobileDetect from 'mobile-detect'

console.log(window.location.hostname)
const componentsBaseURL = window.location.hostname === 'localhost' ? '' : 'https://jstor-labs.github.io/visual-essays'

const defaultComponents = [
  { name: 'mapViewer', src: `${componentsBaseURL}/components/MapViewer.vue`, selectors: ['tag:map'], 'icon': 'fa-map-marker-alt', 'label': 'Map' },
  { name: 'imageViewer', src: `${componentsBaseURL}/components/ImageViewer/index.vue`, selectors: ['tag:image'], 'icon': 'fa-file-image', 'label': 'Images' },
  // { name: 'miradorImageViewer', src: `${componentsBaseURL}/components/MiradorImageViewer.vue`, selectors: ['tag:image'], 'icon': 'fa-images', 'label': 'Images' },
  { name: 'videoPlayer', src: `${componentsBaseURL}/components/videoPlayer.vue`, selectors: ['tag:video'], 'icon': 'fa-video', 'label': 'Videos' },
  // { name: 'person', src: `${componentsBaseURL}/components/EntityViewer.vue`, selectors: ['category:person'], 'icon': 'fa-user', 'label': 'People' },
  // { name: 'entity', src: `${componentsBaseURL}/components/EntityViewer.vue`, selectors: ['tag:entity'], 'icon': 'fa-brackets-curly', 'label': 'Entities' },
  { name: 'network', src: `${componentsBaseURL}/components/Network.vue`, selectors: ['tag:network'], 'icon': 'fa-chart-network', 'label': 'Networks' },
  { name: 'plant-specimen', src: `${componentsBaseURL}/components/PlantSpecimenViewer.vue`, selectors: ['tag:plant-specimen'], 'icon': 'fa-seedling', 'label': 'Plant Specimens' },
  { name: 'essay', component: Essay },
  { name: 'horizontalViewer', component: HorizontalViewer },
  { name: 'verticalViewer', component: VerticalViewer },
  { name: 'entityInfoboxDialog', component: EntityInfoboxDialog },
  { name: 'galleryImageViewer', src: `${componentsBaseURL}/components/ImageViewer/GalleryImageViewer.vue` },
  { name: 'cardsImageViewer', src: `${componentsBaseURL}/components/ImageViewer/CardsImageViewer.vue` },
  { name: 'hiresImageViewer', src: `${componentsBaseURL}/components/ImageViewer/HiresImageViewer.vue` },
  { name: 'entityInfobox', src: `${componentsBaseURL}/components/EntityInfobox.vue` }
]

const components = {}
defaultComponents.forEach(component => components[component.name] = component)

const VERSION = '0.7.1'

console.log(`visual-essays js lib ${VERSION}`)

Vue.component('lingallery', Lingallery)

Vue.mixin({
  computed: {
    activeElement() { return store.getters.activeElement },
    activeElements() { return store.getters.activeElements },
    allItems() { return store.getters.items },
    itemsInActiveElements() { return store.getters.itemsInActiveElements },
    components() { return store.getters.components },
    groups() { return groupItems(itemsInElements(elemIdPath(this.activeElement), this.allItems), store.getters.componentSelectors) },
    // selectedItemID () { return store.getters.selectedItemID }
    // visualizerIsOpen() { return store.getters.visualizerIsOpen }
  }
})

const md = new MobileDetect(window.navigator.userAgent)
const isMobile = md.phone() !== null
const isTouchDevice = md.phone() !== null || md.tablet() !== null

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

// Site components
const getSiteConfig = async () => {
  const response = await fetch('/config')
  const siteConfig = await response.json()
  if (siteConfig.components) {
    siteConfig.components.forEach(cfg => components[cfg.name] = cfg)
  }
}
getSiteConfig()

const initialStateCopy = JSON.parse(JSON.stringify(store.state))

function resetState () {
  store.replaceState(JSON.parse(JSON.stringify(initialStateCopy)))
}

function initApp() {
  console.log('visual-essays.init')

  resetState()

  window.data = []
  document.querySelectorAll('script[type="application/ld+json"]').forEach((scr) => {
    eval(scr.text)
  })

  // Essay components
  window.data.filter(item => item.tag === 'component').forEach(customComponent => {
    components[customComponent.name] = customComponent
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

  for (let [name, component] of Object.entries(components)) {
    if (!component.component) {
      component.component = httpVueLoader(component.src)
    }
    Vue.component(name, component.component)
    if (!component.name) {
      component.name = name
    }
  }

  Vue.prototype.$mirador = mirador

  vm = new Vue({
    template: '<App/>',
    store,
    render: h => h(App),
    vuetify: new Vuetify()
  })
  console.log(`geoJsonCache cache_size=${Object.keys(vm.$store.getters.geoJsonCache).length}`)

  vm.$store.dispatch('setComponents', components)
  console.log('components', vm.$store.getters.components)

  vm.$store.dispatch('setEssayHTML', undefined)

  vm.$store.dispatch('setContent', [])
  vm.$store.dispatch('setItems', [])

  vm.$store.dispatch('setItems', prepItems(window.data.filter(item => item.tag !== 'component')))
  vm.$store.getters.items.forEach(item => console.log(`${item.id} ${item.label || item.title}`, item))

  vm.$store.dispatch('setEssayHTML', document.getElementById('essay').innerHTML)

  const qargs = parseQueryString()
  const essayConfig = vm.$store.getters.items.find(item => item.tag === 'config') || {}
  vm.$store.dispatch('setLayout', isMobile ? 'hc' : (qargs.layout || essayConfig.layout || 'hc' ))
  vm.$store.dispatch('setShowBanner', window.app === undefined && !(qargs.nobanner === 'true' || qargs.nobanner === ''))
  vm.$store.dispatch('setContext', qargs.context || essayConfig.context)
  vm.$store.dispatch('setDebug', qargs.debug === 'true' || qargs.debug === '')
  vm.$store.dispatch('setIsMobile', isMobile)
  vm.$store.dispatch('setIsTouchDevice', isTouchDevice)

  // vm.$store.dispatch('setTrigger', window.triggerPosition || vm.$store.getters.trigger)
  console.log(`layout=${vm.$store.getters.layout} showBanner=${vm.$store.getters.showBanner} context=${vm.$store.getters.context} isMobile=${vm.$store.getters.isMobile} debug=${vm.$store.getters.debug}`)

  if (window.app) {
    window.app.essayConfig = essayConfig
    window.app.libVersion = VERSION
  } else {
    vm.$store.dispatch('setEssayConfig', essayConfig)
  }

  vm.$mount('#essay')
  if (window.app) {
    window.app.isLoaded = true
    window.vm = vm
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