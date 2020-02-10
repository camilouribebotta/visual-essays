import Vue from 'vue'
import Vuetify from 'vuetify'
import httpVueLoader from 'http-vue-loader'
import App from './App.vue'
import store from './store'
import 'leaflet'
import 'scrollmagic/scrollmagic/uncompressed/plugins/debug.addIndicators.js'
import 'leaflet.control.opacity/dist/L.Control.Opacity.css'
import 'leaflet.control.opacity'
import { parseQueryString } from './utils'

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

function initApp() {
  console.log('visual-essays.init')
  window.data = undefined
  window.context = undefined
  console.log('window.data', window.data)

  document.querySelectorAll('script[type="application/ld+json"]').forEach((scr) => {
    eval(scr.text)
    // scr.parentElement.removeChild(scr)
  })
  console.log('window.data', window.data)

  window.customComponents = {}
  if (window.data) {
    window.data.filter(item => item.type === 'component').forEach(item => window.customComponents[item.name] = item)
    console.log('customComponents', window.customComponents)
  }

  Vue.config.productionTip = false
  Vue.config.devtools = true

  Vue.use(Vuetify)
  Vue.use(httpVueLoader)
  Vue.prototype.$L = L

  vm = new Vue({
    template: '<App/>',
    store,
    render: h => h(App),
    vuetify: new Vuetify()
  })
  vm.$store.dispatch('setEssayHTML', undefined)
  vm.$store.dispatch('setContent', [])
  vm.$store.dispatch('setItems', [])
  vm.$store.dispatch('setContext', undefined)
  vm.$store.dispatch('setLayout', 'horizontal')

  if (window.data) {
    vm.$store.dispatch('setItems', window.data.filter(item => item.type !== 'component'))
    console.log('items', vm.$store.getters.items)
  }
  vm.$store.dispatch('setEssayHTML', document.getElementById('essay').innerHTML)

  const qargs = parseQueryString()
  vm.$store.dispatch('setDebug', qargs.debug === 'true' || qargs.debug === '')

  const context = qargs.context || window.context
  if (context) {
    vm.$store.dispatch('setContext', context)
  }
  console.log(`context=${vm.$store.getters.context}`)

  const layout = parseQueryString().layout || window.layout
  if (layout) {
    vm.$store.dispatch('setLayout', layout)
  }
  console.log(`layout=${vm.$store.getters.layout}`)
  
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

// document.addEventListener('DOMContentLoaded', () => { initApp() }, false)

document.addEventListener('DOMContentLoaded', () => {
  let href = window.location.href
  const waitForContent = () => {
    if (vm) {
      if (href !== window.location.href) {
        href = window.location.href
        console.log('remove vm')
        vm = vm.$destroy()
        const essayElem = document.getElementById('essay')
        if (essayElem) {
          essayElem.parentNode.removeChild(essayElem)
        }
      }
    } else {
      const essayElem = document.getElementById('essay')
      if (essayElem && essayElem.innerText.length > 0) {
        initApp()
        vm.$store.getters.items.forEach((item) => {
          if (item.type === 'essay' && item.title) {
            essayElem.title = item.title
            console.log(essayElem.title)
          }
        })
        href = window.location.href
        // console.log(href)
      }
    }
  }
  setInterval(() => waitForContent(), 250)
}, false)
