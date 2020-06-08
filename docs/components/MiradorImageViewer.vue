<template>
  <v-container :style="containerStyle">
    <div id="mirador"></div>
  </v-container>
</template>

<script>

const defaults = {
  canvas: { height: 3000, width: 3000 },
  image: { region: 'full', size: 'full', rotation: '0' },
  iiifServer: 'https://tripleeyeeff-atjcn6za6q-uc.a.run.app'
}

module.exports = {
  name: 'Mirador',
  props: { items: Array, width: Number, height: Number },
  data: () => ({}),
  computed: {
    containerStyle() { return { position: 'relative', width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important' } },
    manifests() {
      return this.items.map(image => {
        return {
          label: image.title, 
          description: image.description, 
          sequences: [{
            canvases: [{
              ...defaults.canvas, ...{ 
              label: image.title, 
              images: [{ 
                ...defaults.image, ...{ 
                url: image.hires || image.url } 
              }]} 
            }]
          }]
        }
      })
    }
  },
  mounted() {
    console.log('Mirador.mounted', this.height, this.width)
    // this.loadImages()
    this.$mirador.viewer({
      id: 'mirador', 
      windows: this.items.map(item => {return {manifestId: item.manifestId}})
    })
  },
  methods: {
    async loadManifest(manifest) {
      return fetch(`${defaults.iiifServer}/presentation/create`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(manifest)
      }).then(resp => resp.json())
    },
    async loadImages() {
      Promise.all(this.manifests.map(manifest => this.loadManifest(manifest)))
      .then(manifests => {
        this.$mirador.viewer({
          id: 'mirador', 
          windows: manifests.map(manifest => {return {manifestId: manifest['@id']}})
        })
      })
    }
  }
}
</script>
