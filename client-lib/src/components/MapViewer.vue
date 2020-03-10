<template>
    <div ref="mapWrapper" class="row wrapper" style="width:100%; margin:0;">
        <div ref="mapWrapperInner">
            <div ref="map" id="lmap" class="lmap" style="margin:0;"></div>
        </div>
    </div>
</template>

<script>
export default {
  name: 'MapViewer',
  props: {
    items: { type: Array, default: () => ([]) },
    selected: { type: String },
    maxWidth: { type: Number, default: 800 },
    maxHeight: { type: Number, default: 800 }
  },
  data: () => ({
    map: null,
    mapLayers: {
      baseLayer: null,
      mapwarper: {},
      markerGroups: [],
      geojson: {}
    },
    controls: {},
    featuresById: {}
  }),
  computed: {
    mapDef() { return this.items[0] },
    activeElements() { return this.$store.getters.activeElements },
    itemsInActiveElements() { return this.$store.getters.itemsInActiveElements },
    entities() { return this.itemsInActiveElements.filter(item => item.type === 'entity') },
    locations() { return this.entities.filter(entity => entity.coords) },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
  },
  mounted() {
    console.log(`${this.$options.name} mounted maxWidth=${this.maxWidth}`)
    this.$nextTick(() => { this.createBaseMap() })
  },
  methods: {
    createBaseMap() {
      this.positionMapContainer()
      this.map = this.$L.map('lmap', {zoomSnap: 0.1})
      this.map.setView(this.mapDef.center, this.mapDef.zoom || 10)
      this.mapLayers.baseLayer = this.$L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
      this.map.addLayer(
        this.mapLayers.baseLayer,
        {
          maxZoom: 18,
          attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }
      )
      this.updateLayers()
    },
    positionMapContainer() {
      if (this.$refs.map) {
        const calculatedContainerHeight = this.viewport.height/2
        // const mapHeight = calculatedContainerHeight < this.maxHeight ? calculatedContainerHeight : this.maxHeight
        const mapHeight = this.maxHeight
        const mapWidth = this.viewport.width < this.maxWidth ? this.viewport.width : this.maxWidth
        const wrapperWidth = this.$refs.mapWrapper.clientWidth
        // this.$refs.map.style.height = `${mapHeight - 52}px`
        this.$refs.map.style.height = `${mapHeight}px`
        this.$refs.map.style.width = `${mapWidth}px`
        console.log(`wrapperWidth=${wrapperWidth} calculatedContainerHeight=${calculatedContainerHeight} mapHeight=${mapHeight} mapWidth=${mapWidth}`)
        // center the map
        this.$refs.mapWrapperInner.style.paddingTop = 0
        this.$refs.mapWrapperInner.style.paddingBottom = 0
        this.$refs.mapWrapperInner.style.paddingLeft = `${(wrapperWidth - mapWidth)/2}px`
      }
    },
    setLayers() {
      Object.entries(this.mapDef.layers).forEach(mapLayer => {
        const layerType = mapLayer[0]
        const layerValues = mapLayer[1]
        const currentLayers = {}
        layerValues.forEach(def => {
          if (this.mapLayers[layerType][def.id]) {
            currentLayers[def.id] = this.mapLayers[layerType][def.id]
          } else {
            const layer = layerType === 'mapwarper'
                ? this.$L.tileLayer(`https://mapwarper.net/maps/tile/${def['mapwarper-id']}/{z}/{x}/{y}.png`)
                : this.$L.geoJSON(def.geojson, { onEachFeature: this.onEachFeature } )
            if (layerType !== 'mapwarper') {
              layer.bindPopup(this.makePopup(def))
            }
            currentLayers[def.id] = {
              id: def.id,
              name: def.title,
              active: (def.active || 'false') === 'true',
              layer
            }
          }
        })
        for (const layerId in this.mapLayers[layerType]) {
          if (!currentLayers[layerId]) {
            this.mapLayers[layerType][layerId].layer.removeFrom(this.map)
          }                
        }
        this.mapLayers[layerType] = currentLayers
      })
      // console.log(this.mapLayers)
    },
    setControls() {
      const baseLayers = {
        base: this.mapLayers.baseLayer
      }
      const allLayers = {}
      const fadeableLayers = {}
      Object.entries(this.mapDef.layers).forEach(mapLayer => {
        const layerType = mapLayer[0]
        const layerValues = mapLayer[1]
        layerValues.forEach(layerDef => {
          const layer = this.mapLayers[layerType][layerDef.id]
          allLayers[layer.name] = layer.layer
          if (layerType === 'mapwarper') {
            fadeableLayers[layer.name] = layer.layer
          }
        })
      })
      for (const layerId in this.mapLayers.markerGroups) {
        const layer = this.mapLayers.markerGroups[layerId]
        allLayers[layer.name] = this.mapLayers.markerGroups[layerId].layer
      }

      if (this.controls.layers) {
        this.map.removeControl(this.controls.layers)
      }
      this.controls.layers =
        this.$L.control.layers(
          {}, // baseLayers,
          allLayers, 
          { collapsed: true } //options
        ).addTo(this.map)
      
      // opacity control
      if (this.controls.opacity) {
        this.map.removeControl(this.controls.opacity)
      }
      this.controls.opacity =
          this.$L.control.opacity(
              fadeableLayers,
              {
                  // label: 'Layers Opacity',
                  collapsed: true 
              }
          ).addTo(this.map)
    },
    getLocationMarkers() {
      const markers = []
      this.locations.forEach((location) => {
        const marker = this.$L.marker(location.coords[0]).bindPopup(this.makePopup(location))
        markers.push(marker)
        this.featuresById[location.id] = marker
      })
      return markers
    },
    setMarkerGroups() {
      const currentMarkerGroups = {
        locations: {
          name: 'Locations',
          active: true,
          layer: this.$L.layerGroup([...this.getLocationMarkers()])
        }
      }
      for (const groupName in this.mapLayers.markerGroups) {
        const markerGroup = this.mapLayers.markerGroups[groupName]
        this.map.removeLayer(markerGroup.layer)
      }
      this.mapLayers.markerGroups = currentMarkerGroups
    },
    updateLayers() {
      if (this.map) {
        this.setLayers()
        this.setMarkerGroups()
        this.sync()
      }
    },
    sync() {
      if (this.map) {
        Object.entries(this.mapDef.layers).forEach(mapLayer => {
          const layerType = mapLayer[0]
          const layerValues = mapLayer[1]
          layerValues.forEach(layerDef => {
            const layer = this.mapLayers[layerType][layerDef.id]
            if (layer.active) {
              this.map.addLayer(layer.layer)
            } else {
              this.map.removeLayer(layer.layer)
            }
          })
        })
        for (const groupName in this.mapLayers.markerGroups) {
          const markerGroup = this.mapLayers.markerGroups[groupName]
          if (markerGroup.active) {
            this.map.addLayer(markerGroup.layer)
          } else {
            this.map.removeLayer(markerGroup.layer)
          }
        }
        this.setControls()
      }
    },
    makePopup(item) {
      let pu = `<h1>${item.label || item.title}</h1>`
      if (item.images) {
        pu += `<img src="${item.images[0]}">`
        pu = `<div style="width: 125px !important; height:135px !important;">${pu}</div>`
      }
      return pu
    }
  },
  watch: {
    selected: {
      handler: function (value, prior) {
        if (this.featuresById[this.selected]) {
          this.featuresById[this.selected].openPopup()
        }
      },
      immediate: true
    },
    viewport: {
      handler: function (value, prior) {
      },
      immediate: true
    },
    activeElements: {
      handler: function () {
        this.updateLayers()
      },
      immediate: false
    },
    mapDef: {
      handler: function (value, prior) {
        if (this.$refs.map) {
          if (this.items.length === 0) {
              this.$refs.mapWrapper.style.display = 'none'
          } else {
            if (this.map) {
              if (this.items.length > 0) {
                const curMap = this.items[0]
                // this.map.setView(curMap.center, curMap.zoom || 10)
                this.map.flyTo(curMap.center, curMap.zoom || 10)
              }
            } else {
              this.createBaseMap()
            }
            this.$refs.mapWrapper.style.display = 'block'
          }
        }
      },
      immediate: true
    }
  }

}

</script>

<style>

  .wrapper {
    display: inherit;
  }
  
  .lmap {
    z-index: 1;
    width: 100%;
  }

  .leaflet-interactive {
    fill-opacity: 0;
  }

  .leaflet-container {
    background: white !important;
  }

  /*
  .leaflet-popup-content-wrapper {
    height: 150px;
    width: 150px;
  }
  */
  .leaflet-popup-content-wrapper h1 {
    font-size: 14px;
    text-align: center;
  }
  .leaflet-popup-content-wrapper img {
    /* object-fit:
       fill = stretched to fit box
       contain = maintain its aspect ratio, scaled fit within the element’s box, letterboxed if needed
       cover = fills entire box, maintains aspect ration, clipped to fit
       none = content not resized
       scale-down = same as none or contain, whichever is smaller
    */
    object-fit: contain; 
    width: 125px;
    height: 120px;
    /* 
    padding: 2px 10px 2px 0;
    float: left;
    */
    vertical-align: top;
  }    
  

</style>
