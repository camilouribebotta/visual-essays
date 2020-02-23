import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const state = {
  baseUrl: undefined,
  markup: 'markdown',
  title: undefined,
  banner: undefined,
  html: undefined,
  pages: {},
  viewport: null,
  spacerHeight: 0,
  isMobile: false,
  isIos: false,
  isInStandaloneMode: false,
  installMessageDismissed: false,
  isOnline: false,
  logMessages: {
    debug: [],
    info: [],
    warning: [],
    error: []
  }
}

const mutations = {
  setBaseUrl(state, baseUrl) { state.baseUrl = baseUrl },
  setMarkup(state, markup) { state.markup = markup },
  setTitle(state, title) { state.title = title },
  setBanner(state, banner) { state.banner = banner },
  setHtml(state, html) { state.html = html },
  setPage(state, page) { state.pages = { ...state.pages, ...page } },
  setViewport(state, viewport) { state.viewport = viewport },
  setSpacerHeight(state, height) { state.spacerHeight = height },
  setIsMobile(state, isMobile) { state.isMobile = isMobile },
  setIsIos(state, isIos) { state.isIos = isIos },
  setIsInStandaloneMode(state, isInStandaloneMode) { state.isInStandaloneMode = isInStandaloneMode },
  setInstallMessageDismissed(state, installMessageDismissed) { state.installMessageDismissed = installMessageDismissed },
  setIsOnline(state, isOnline) { state.isOnline = isOnline },
  pushLogMessage (state, payload) {
    const logMessagesCopy = { ...state.logMessages }
    const messages = [ ...logMessagesCopy[payload.level], payload.text]
    logMessagesCopy[payload.level] = messages.length > 5 ? messages.slice(messages.length - 5, messages.length) : messages
    state.logMessages = logMessagesCopy
  },
  popLogMessage (state, level) {
    if (state.logMessages[level].length > 0) {
      const logMessagesCopy = { ...state.logMessages }
      const messages = [ ...logMessagesCopy[level] ]
      messages.shift()
      logMessagesCopy[level] = messages
      state.logMessages = logMessagesCopy
    }
  },
  clearLogMessages (state, level) {
    let logMessagesCopy = { ...state.logMessages }
    if (level) {
      logMessagesCopy[level] = []
    } else {
      logMessagesCopy = {
        debug: [],
        info: [],
        warning: [],
        error: []
      }
    }
    state.logMessages = logMessagesCopy
  }
}

const actions = {
  nuxtServerInit(vuexContext, context) {
    // console.log('nuxtServerInit')
  },
  setBaseUrl: ({ commit }, baseUrl) => commit('setBaseUrl', baseUrl),
  setMarkup: ({ commit }, markup) => commit('setMarkup', markup),
  setViewport: ({ commit }, viewport) => commit('setViewport', viewport),
  setTitle: ({ commit }, title) => commit('setTitle', title),
  setBanner: ({ commit }, banner) => commit('setBanner', banner),
  setHtml: ({ commit }, html) => commit('setHtml', html),
  setPage: ({ commit }, page) => commit('setPage', page),
  setSpacerHeight: ({ commit }, height) => commit('setSpacerHeight', height),
  setIsMobile: ({ commit }, isMobile) => commit('setIsMobile', isMobile),
  setIsIos: ({ commit }, isIos) => commit('setIsIos', isIos),
  setIsInStandaloneMode: ({ commit }, isInStandaloneMode) => commit('setIsInStandaloneMode', isInStandaloneMode),
  setInstallMessageDismissed: ({ commit }, installMessageDismissed) => commit('setInstallMessageDismissed', installMessageDismissed),
  setIsOnline: ({ commit }, isOnline) => commit('setIsOnline', isOnline),
  pushLogMessage: ({ commit }, payload) => commit('pushLogMessage', payload),
  popLogMessage: ({ commit }, level) => commit('popLogMessage', level),
  clearLogMessages: ({ commit }, level) => commit('clearLogMessages', level),
}

const getters = {
  baseUrl: state => state.baseUrl,
  markup: state => state.markup,
  title: state => state.title,
  banner: state => state.banner,
  pages: state => state.pages,
  html: state => state.html,
  viewport: state => state.viewport,
  spacerHeight: state => state.spacerHeight,
  isMobile: state => state.isMobile,
  isIos: state => state.isIos,
  isInStandaloneMode: state => state.isInStandaloneMode,
  installMessageDismissed: state => state.installMessageDismissed,
  showInstallMessage: state => state.isIos && !state.isInStandaloneMode && !state.installMessageDismissed,
  logMessages: state => state.logMessages
}

export default () => new Vuex.Store({
  state,
  getters,
  actions,
  mutations
})
