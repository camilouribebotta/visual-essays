export default ({ app }, inject) => {
  
    app.store.dispatch('setBaseUrl', process.env.base_url )
    app.store.dispatch('setMarkup', process.env.markup )
    app.store.dispatch('setPage', {'index': process.env.index} )
    app.store.dispatch('setPage', {'about': process.env.about} )
    app.store.dispatch('setPage', {'help': process.env.help} )
    app.store.dispatch('setPage', {'contact': process.env.contact} )
  }