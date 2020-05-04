import Vue from 'vue'
import Vuex from 'vuex'
import { itemsInElements } from '../utils'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    essayHTML: undefined,
    layout: 'vtl',
    showBanner: true,
    headerSize: 96,
    contentStartPos: 0,
    triggerOffset: 300,
    debug: false,
    context: undefined,
    content: [],
    items: [],
    activeElements: [],
    itemsInActiveElements: [],
    selectedItemID: null,
    height: 0,
    width: 0,
    topMargin: 0,
    progress: 0,
    geoJsonCache: {}
  },
  mutations: {
    setEssayHTML (state, html) { state.essayHTML = html },
    setLayout (state, layout) { state.layout = layout },
    setShowBanner (state, showBanner) { state.showBanner = showBanner},
    setHeaderSize (state, headerSize) { state.headerSize = headerSize},
    setContentStartPos (state, pos) { state.contentStartPos = pos },
    setTriggerOffset (state, triggerOffset) { state.triggerOffset = triggerOffset },
    setContext (state, context) { state.context = context },
    setDebug (state, debug) { state.debug = debug },
    setContent (state, elems) { state.content = elems },
    setItems (state, items) { state.items = items },
    setActiveElements (state, elems) {
      state.activeElements = elems
      state.itemsInActiveElements = itemsInElements(state.activeElements, state.items)
    },
    setSelectedItemID (state, id) { state.selectedItemID = id },
    updateItem (state, item) {
      state.items = [ 
        ...state.items.filter(c => c.id !== item.id),
        { ...state.items.find(c => c.id === item.id), ...item }
      ]
    },
    setViewport(state, viewport) { 
      state.height = viewport.height
      state.width = viewport.width
    },
    setTopMargin (state, height) { state.topMargin = height },
    setProgress (state, progress) {
      state.progress = progress
      if (window.app) {
        window.app.progress = state.progress
      }
    },
    addToGeoJsonCache (state, geoJson) { state.geoJsonCache = { ...state.geoJsonCache, ...geoJson} }
  },
  actions: {
    setEssayHTML: ({ commit }, html) => commit('setEssayHTML', html),
    setLayout: ({ commit }, layout) => commit('setLayout', layout),
    setShowBanner: ({ commit }, showBanner) => commit('setShowBanner', showBanner),
    setHeaderSize: ({ commit }, headerSize) => commit('setHeaderSize', headerSize),
    setContentStartPos: ({ commit }, pos) => commit('setContentStartPos', pos),
    setTriggerOffset: ({ commit }, triggerOffset) => commit('setTriggerOffset', triggerOffset),
    setContext: ({ commit }, context) => commit('setContext', context),
    setDebug: ({ commit }, debug) => commit('setDebug', debug),
    setContent: ({ commit }, content) => commit('setContent', content),
    setItems: ({ commit }, items) => commit('setItems', items),
    setActiveElements: ({ commit }, elems) => commit('setActiveElements', elems),
    setSelectedItemID: ({ commit }, id) => commit('setSelectedItemID', id),
    updateItem: ({ commit }, entity) => commit('updateItem', entity),
    setViewport: ({ commit }, viewport) => commit('setViewport', viewport),
    setTopMargin: ({ commit }, height) => commit('setTopMargin', height),
    setProgress: ({ commit }, progress) => commit('setProgress', progress),
    addToGeoJsonCache: ({ commit }, geoJson) => commit('addToGeoJsonCache', geoJson)
  },
  getters: {
    layout: state => state.layout,
    showBanner: state => state.showBanner,
    headerSize: state => state.headerSize,
    contentStartPos: state => state.contentStartPos,
    triggerOffset: state => state.triggerOffset,
    essayHTML: state => state.essayHTML,
    context: state => state.context,
    debug: state => state.debug,
    content: state => state.content,
    items: state => state.items,
    activeElements: state => state.activeElements,
    activeElement: (state) => state.activeElements.length > 0 ? state.activeElements[0] : undefined,
    itemsInActiveElements: state => state.itemsInActiveElements,
    selectedItemID: state => state.selectedItemID,
    height: state => state.height,
    width: state => state.width,
    topMargin: state => state.topMargin,
    progress: state => state.progress,
    geoJsonCache: state => state.geoJsonCache
  },
  modules: {
  }
})
