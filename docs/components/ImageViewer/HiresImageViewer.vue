<template>
  <div>
    <v-dialog v-model="isOpen" fullscreen @click:outside="close">
      <v-card dark>
        <v-card-actions class="close-button">
          <v-btn @click="close" color="primary">Exit</v-btn>
        </v-card-actions>
        <v-card-text>
            <div id="mirador"></div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>

module.exports = {
  name: 'HiresImageViewer',
  props: {
    items: Array,
    isOpen: false,
  },
  data: () => ({
    scale: 0.9
  }),
  computed: {
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
    width() { return this.viewport.width * this.scale },
    height() { return this.viewport.height * this.scale - 150},
    containerStyle() { return { position: 'relative', width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important' } },
  },
  mounted() {
    console.log(`HiresImageViewer.mounted: width=${this.width} height=${this.height}`)
  },
  methods: {
    close() {
      this.$emit('close')
    },
    load() {
      console.log('load', document.getElementById('mirador'))
      this.$mirador.viewer({
        id: 'mirador',
        windows: this.items.map(item => {return { manifestId: item.manifest } }),
        workspace: {
          type: 'mosaic'
        },
        workspaceControlPanel: {
          enabled: true
        },
        window: {
          allowClose: false, // Configure if windows can be closed or not
          allowFullscreen: true, // Configure to show a "fullscreen" button in the WindowTopBar
          allowMaximize: true, // Configure if windows can be maximized or not
          allowTopMenuButton: true, // Configure if window view and thumbnail display menu are visible or not
          allowWindowSideBar: true, // Configure if side bar menu is visible or not
          authNewWindowCenter: 'parent', // Configure how to center a new window created by the authentication flow. Options: parent, screen
          defaultSideBarPanel: 'info', // Configure which sidebar is selected by default. Options: info, attribution, canvas, annotations, search
          defaultSidebarPanelHeight: 201,  // Configure default sidebar height in pixels
          defaultSidebarPanelWidth: 235, // Configure default sidebar width in pixels
          defaultView: 'single',  // Configure which viewing mode (e.g. single, book, gallery) for windows to be opened in
          hideWindowTitle: false, // Configure if the window title is shown in the window title bar or not
          showLocalePicker: false, // Configure locale picker for multi-lingual metadata
          sideBarOpenByDefault: false, // Configure if the sidebar (and its content panel) is open by default
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
    }
  },
  watch: {
    isOpen: {
      handler: function () {
        if (this.isOpen) {
          this.$nextTick(() => this.load())
        }
      },
      immediate: true
    }
  }
}
</script>

<style scoped>
  .v-overlay {
    opacity: 100 !important;
  }

  .theme--dark.v-sheet {
    background-color: black;
  }

  .card-title {
    padding-top: 16px !important;
  }

  .v-card__title {
    background-color: #fff;
    padding-left: 16px !important;
    border-bottom: 1px solid #acb0bc;
    color: #000;
  }

  .close-button {
    display: inline-block;
    position: absolute;
    top: 3px;
    right: 0;

  }
</style>
