import Vue from 'vue'
import Vuetify from 'vuetify'
import httpVueLoader from 'http-vue-loader'
import App from './App.vue'
import store from './store'
import 'leaflet'
// import '../assets/styles/main.css'

// import 'leaflet/dist/leaflet.css'
import 'leaflet.control.opacity/dist/L.Control.Opacity.css'
import 'leaflet.control.opacity'

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

// Parses query arguments in request url 
function parseQueryString(queryString) {
  queryString = queryString || window.location.search
  const dictionary = {}
  try {
    if (queryString.indexOf('?') === 0) {
      queryString = queryString.substr(1)
    }
    const parts = queryString.split('&')
    for (let i = 0; i < parts.length; i++) {
      const p = parts[i]
      const keyValuePair = p.split('=')
      if (keyValuePair[0] !== '') {
        const key = keyValuePair[0]
        if (keyValuePair.length === 2) {
          let value = keyValuePair[1]
          // decode URI encoded string
          value = decodeURIComponent(value)
          value = value.replace(/\+/g, ' ')
          dictionary[key] = value
        } else {
          dictionary[key] = ''
        }
      }
    }
  } catch (err) {
    console.log(err)
  }
  return dictionary
}

function initApp() {
  console.log('essay-utils.init')

  const vueAppElem = document.createElement('div')
  vueAppElem.id = 'app1'
  document.body.appendChild(vueAppElem)
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
  vm.$mount('#app1')

  document.querySelectorAll('script[type="application/ld+json"]').forEach((scr) => {
    eval(scr.text)
  })

  const context = parseQueryString().context || window.context
  if (context) {
    vm.$store.dispatch('setContext', window.context)
  }
  console.log(`context=${vm.$store.getters.context}`)

  if (window.data) {
    vm.$store.dispatch('setItems', window.data)
  }
  console.log('items', vm.$store.getters.items)

  setViewport()
  window.addEventListener('resize', () => {
    rtime = new Date()
    if (timeout === false) {
      timeout = true
      setTimeout(resizeend, delta)
    }
  })
}

document.addEventListener('DOMContentLoaded', () => {
  let href = window.location.href
  const waitForContent = () => {
    if (vm) {
      if (href !== window.location.href) {
        href = window.location.href
        vm = vm.$destroy()
      }
    } else {
      const esssayElem = document.getElementById('essay')
      if (esssayElem && esssayElem.innerText.length > 0) {
        initApp()
        href = window.location.href
        console.log(href)
      }
    }
  }
  setInterval(() => waitForContent(), 250)
}, false)
