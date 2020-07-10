<template>
  <div :id="`mirador-${seq}`" :style="containerStyle"></div>
</template>

<script>
// Mirador config options are defined at https://github.com/ProjectMirador/mirador/blob/master/src/config/settings.js

module.exports = {
  name: 'MiradorImageViewer',
  props: {
    seq: { type: Number, default: 1 },
    autohideToolbar: { type: Boolean, default: false },
    items: { type: Array, default: function(){ return []} },
    width: { type: Number, default: 1000 }, 
    height: { type: Number, default: 1000 }
  },
  data: () => ({
    windows: undefined,
    viewer: undefined
  }),
  computed: {
    containerStyle() { return { position: 'relative', width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important' } }
  },
  mounted() {
    console.log(`MiradorImageViewer.mounted: seq=${this.seq} height=${this.height} width=${this.width}`, this.items)
    this.windows = this.items.map(item => {return { manifestId: item.manifest } }) 
    this.viewer = this.$mirador.viewer({
      id: `mirador-${this.seq}`,
      selectedTheme: 'light',
      // windows: this.windows,
      workspace: {
        type: 'mosaic'
      },
      workspaceControlPanel: {
        enabled: false
      },
      window: {
        allowClose: false, // Configure if windows can be closed or not
        allowFullscreen: true, // Configure to show a "fullscreen" button in the WindowTopBar
        allowMaximize: false, // Configure if windows can be maximized or not
        allowTopMenuButton: false, // Configure if window view and thumbnail display menu are visible or not
        allowWindowSideBar: true, // Configure if side bar menu is visible or not
        authNewWindowCenter: 'parent', // Configure how to center a new window created by the authentication flow. Options: parent, screen
        defaultSideBarPanel: 'info', // Configure which sidebar is selected by default. Options: info, attribution, canvas, annotations, search
        defaultSidebarPanelHeight: 201,  // Configure default sidebar height in pixels
        defaultSidebarPanelWidth: 235, // Configure default sidebar width in pixels
        defaultView: 'single',  // Configure which viewing mode (e.g. single, book, gallery) for windows to be opened in
        hideWindowTitle: false, // Configure if the window title is shown in the window title bar or not
        showLocalePicker: false, // Configure locale picker for multi-lingual metadata
        sideBarOpenByDefault: true, // Configure if the sidebar (and its content panel) is open by default
        panels: { // Configure which panels are visible in WindowSideBarButtons
          info: true,
          attribution: true,
          canvas: true,
          annotations: true,
          search: true,
        },
        views: [
          { key: 'single', behaviors: ['individuals'] },
          { key: 'book', behaviors: ['paged'] },
          { key: 'scroll', behaviors: ['continuous'] },
          { key: 'gallery' },
        ]
      }
    })
    this.viewer.store.dispatch(this.viewer.actions.addWindow(this.windows[0]))

    if (this.autohideToolbar) {
      document.querySelectorAll('.mirador-window-top-bar').forEach(topBar => topBar.style.display = 'none')
      document.querySelectorAll(`#mirador-${this.seq}`).forEach(osd => {
        osd.addEventListener('mouseenter', (e) => {
          document.querySelectorAll('.mirador-window-top-bar').forEach(topBar => topBar.style.display = 'flex')
        })
        osd.addEventListener('mouseleave', (e) => {
          document.querySelectorAll('.mirador-window-top-bar').forEach(topBar => topBar.style.display = 'none')
        })
      })
    }
  },
  watch: {
    items: {
      handler: function () {
        Object.keys(this.viewer.store.getState().windows).forEach(windowKey => this.viewer.store.dispatch(this.viewer.actions.removeWindow(windowKey)))
        let windows = this.items.map(item => {return { manifestId: item.manifest } })
        this.viewer.store.dispatch(this.viewer.actions.addWindow(windows[0]))
      },
      immediate: false
    }
  }
}
</script>
