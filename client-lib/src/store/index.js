import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    context: undefined,
    content: [],
    items: [],
    activeElements: [],
    selectedEntityQID: null,
    height: 0,
    width: 0
  },
  mutations: {
    setContext (state, context) { state.context = context },
    setContent (state, elems) { state.content = elems },
    setItems (state, items) { state.items = items },
    setActiveElements (state, elems) { state.activeElements = elems },
    setSelectedEntityQID (state, qid) { state.selectedEntityQID = qid },
    updateItem (state, item) {
      state.items = [ 
        ...state.items.filter(c => c.id !== item.id),
        { ...state.items.find(c => c.id === item.id), ...item }
      ]
    },
    setViewport(state, viewport) { 
      state.height = viewport.height
      state.width = viewport.width
    }
  },
  actions: {
    setContext: ({ commit }, context) => commit('setContext', context),
    setContent: ({ commit }, elems) => commit('setContent', elems),
    setItems: ({ commit }, items) => commit('setItems', items),
    setActiveElements: ({ commit }, elems) => commit('setActiveElements', elems),
    setSelectedEntityQID: ({ commit }, qid) => commit('setSelectedEntityQID', qid),
    updateItem: ({ commit }, entity) => commit('updateItem', entity),
    setViewport: ({ commit }, viewport) => commit('setViewport', viewport)
  },
  getters: {
    context: state => state.context,
    content: state => state.content,
    items: state => state.items,
    activeElements: state => state.activeElements,
    activeElement: (state) => state.activeElements.length > 0 ? state.activeElements[0] : null,
    itemsInActiveElements(state) {
      const items = {}
      state.activeElements.forEach((elem) => {
        (elem.items || []).forEach(item => items[item.id] = item)
      })
      return Object.values(items)
    },
    selectedEntityQID: state => state.selectedEntityQID,
    height: state => state.height,
    width: state => state.width
  },
  modules: {
  }
})
