import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    essayHTML: undefined,
    layout: 'horizontal',
    visualizerIsOpen: false,
    debug: false,
    context: undefined,
    content: [],
    items: [],
    activeElements: [],
    itemsInActiveElements: [],
    selectedItemID: null,
    height: 0,
    width: 0,
    topMargin: 0
  },
  mutations: {
    setEssayHTML (state, html) { state.essayHTML = html },
    setLayout (state, layout) { state.layout = layout },
    setVisualizerIsOpen (state, isOpen) { state.visualizerIsOpen = isOpen },
    setContext (state, context) { state.context = context },
    setDebug (state, debug) { state.debug = debug },
    setContent (state, elems) { state.content = elems },
    setItems (state, items) { state.items = items },
    setActiveElements (state, elems) {
      state.activeElements = elems
      const items = []
      const itemIds = new Set()
      state.activeElements.forEach(activeElem => {
        state.items
        .filter(item => item.part_of && item.part_of.has(activeElem))
        .filter(item => !itemIds.has(item.id))
        .forEach((item) => {
          itemIds.add(item.id)
          items.push(item)
        })
      })
      state.itemsInActiveElements = Object.values(items)
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
    setTopMargin (state, height) { state.topMargin = height }
  },
  actions: {
    setEssayHTML: ({ commit }, html) => commit('setEssayHTML', html),
    setLayout: ({ commit }, layout) => commit('setLayout', layout),
    setVisualizerIsOpen: ({ commit }, isOpen) => commit('setVisualizerIsOpen', isOpen),
    setContext: ({ commit }, context) => commit('setContext', context),
    setDebug: ({ commit }, debug) => commit('setDebug', debug),
    setContent: ({ commit }, content) => commit('setContent', content),
    setItems: ({ commit }, items) => commit('setItems', items),
    setActiveElements: ({ commit }, elems) => commit('setActiveElements', elems),
    setSelectedItemID: ({ commit }, id) => commit('setSelectedItemID', id),
    updateItem: ({ commit }, entity) => commit('updateItem', entity),
    setViewport: ({ commit }, viewport) => commit('setViewport', viewport),
    setTopMargin: ({ commit }, height) => commit('setTopMargin', height)
  },
  getters: {
    layout: state => state.layout,
    essayHTML: state => state.essayHTML,
    visualizerIsOpen: state => state.visualizerIsOpen,
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
    topMargin: state => state.topMargin
  },
  modules: {
  }
})
