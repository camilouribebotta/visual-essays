<template>
  <v-container :style="outerContainerStyle">
    <v-card flat>
      <v-tabs
        v-model="tab"
        background-color="primary"
        dark
      >
        <v-tab
          v-for="specimens in specimensByTaxon"
          :key="specimens.id"
        >
          {{ specimens.taxonName }}
        </v-tab>
      </v-tabs>

      <v-tabs-items v-model="tab">
        <v-tab-item
          v-for="specimens in specimensByTaxon"
          :key="specimens.id"
        >
          <v-card flat>
            <v-card-text flat :style="innerContainerStyle">
              <image-viewer
                :items="specimens.specimens"
                :width="width"
                :height="height - 46"
                initial-mode="default"
                default-fit="cover">
              </image-viewer>
            </v-card-text>
          </v-card>
        </v-tab-item>
      </v-tabs-items>
    </v-card>
  </v-container>
</template>

<script>
  const defaults = {
    canvas: { height: 3000, width: 3000 },
    image: { region: 'full', size: 'full', rotation: '0' },
    iiifServer: 'https://tripleeyeeff-atjcn6za6q-uc.a.run.app'
  }

  module.exports = {
    name: 'plant-specimens',
    props: { items: Array, width: Number, height: Number },
    data: () => ({
      tab: undefined,
      specimensByTaxon: []
    }),
    computed: {
      outerContainerStyle() { return { width: `${this.width}px`, height: `${this.height}px`, padding: 0 } },
      innerContainerStyle() { return { height: `${this.height - 48}px`, padding: 0, overflowY: 'auto !important' } },
    },
    mounted() {
      this.items.forEach(item => this.getSpecimenMetadata(item))
    },
    methods: {
      async specimensDataForItem(item) {
        if (item.specimensData) {
          this.specimensByTaxon = [...this.specimensByTaxon, item.specimensData]
        } else {
          console.log(item)
          const args = Object.keys(item).filter(arg => ['max', 'reverse'].includes(arg)).map(arg => `${arg}=${item[arg]}`)
          if (item.label) {
            const url = `https://plant-humanities.app/specimens/${item.label.replace(/ /, '_')}` + (args ?  `?${args.join('&')}` : '')
            console.log('getSpecimenMetadata', item)
            item.specimensData = fetch(url)
              .then(resp => { console.log(resp); return resp.json()})
              .then(specimensData => {
                item.specimensData = specimensData;
                item.specimensData.caption = item.label
                item.specimensData.specimens.forEach(specimen => {
                  const defaultImage = specimen.images.find(img => img.type === 'default')
                  const hiresImage = specimen.images.find(img => img.type === 'best')
                  specimen.url = defaultImage.url
                  specimen.hires = hiresImage.url
                  specimen.title = specimen.description
                  if (!specimen.manifest) {
                    specimen.manifest = this.getManifest(specimen)
                    //this.$store.dispatch('updateItem', item)
                  }
                })
                this.specimensByTaxon = [...this.specimensByTaxon, item.specimensData]
                this.$store.dispatch('updateItem', item)
                console.log('md', item.specimensData)
              })
          }
        }
        return item.specimensData
      },
      getSpecimenMetadata(item) {
        this.specimensDataForItem(item)
      },
      getManifest(specimen) {
        const manifest = {
          label: specimen.caption, 
          description: specimen.description, 
          sequences: [{
            canvases: [{
              ...defaults.canvas, ...{ 
              label: specimen.caption, 
              images: [{ 
                ...defaults.image, ...{ 
                url: specimen.hires || specimen.url } 
              }]} 
            }]
          }]
        }
        console.log('getManifest', specimen)
        return fetch(`${defaults.iiifServer}/presentation/create`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(manifest)
        }).then(resp => resp.json())
      }
    }
  }
</script>
