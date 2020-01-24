<template>
    <div ref="mapWrapper" class="row wrapper">
        <div ref="mapWrapperInner" class="col-md-9">
            <div ref="map" id="map" class="lmap" style="margin:0"></div>
        </div>
    </div>
</template>

<script>
export default {
  name: 'Map',
  props: {
    maxWidth: { type: Number, default: 800 },
    maxHeight: { type: Number, default: 800 }
  },
  data: () => ({
    map: null,
    mapLayers: {
      baseLayer: null,
      mapWarper: {},
      markerGroups: [],
      tile: {},
      geoJSON: {}
    },
    controls: {},
    featuresById: {}
  }),
  computed: {
    selectedItemID () { return this.$store.getters.selectedItemID },
    activeElements() { return this.$store.getters.activeElements },
    activeElement() { return this.$store.getters.activeElements.length > 0 ? this.$store.getters.activeElements[0] : null },
    itemsInActiveElements() { return this.$store.getters.itemsInActiveElements },
    mapsInActiveElements() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'map') },
    entities() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'entity') },
    locations() { return this.entities.filter(entity => entity.coords) },
    layerDefinitions() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'map-layer') },
    mapwarperLayerDefs() { return this.layerDefinitions.filter(layer => layer['mapwarper-id']) },
    geojsonLayerDefs() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'geojson') },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} }
  },
  mounted() {
    this.$nextTick(() => { this.createBaseMap() })
  },
  methods: {
    createBaseMap() {
      if (this.mapsInActiveElements.length > 0) {
        this.positionMapContainer()
        const mapDef = this.mapsInActiveElements[this.mapsInActiveElements.length - 1]
        this.map = this.$L.map('map', {zoomSnap: 0.1})
        this.map.setView(mapDef.center, mapDef.zoom || 10)
        this.mapLayers.baseLayer = this.$L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png')
        this.map.addLayer(
          this.mapLayers.baseLayer,
          {
            maxZoom: 18,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          }
        )
        this.updateLayers()
      }
    },
    positionMapContainer() {
      if (this.$refs.map) {
        const calculatedContainerHeight = this.viewport.height/2
        const mapHeight = calculatedContainerHeight < this.maxHeight ? calculatedContainerHeight : this.maxHeight
        this.$refs.map.style.height = `${mapHeight - 52}px`
        const mapWidth = this.viewport.width < this.maxWidth ? this.viewport.width : this.maxWidth
        this.$refs.map.style.width = `${mapWidth}px`
        // center the map
        this.$refs.mapWrapperInner.style.paddingTop = 0
        this.$refs.mapWrapperInner.style.paddingBottom = 0
        this.$refs.mapWrapperInner.style.paddingLeft = `${(this.viewport.width - mapWidth)/2+12}px`
        //this.$refs.mapWrapperInner.style.paddingRight = `${(this.viewport.width - mapWidth)/2}px`
        // console.log(`positionMapContainer: mapHeight=${this.$refs.map.style.height} mapWidth=${this.$refs.map.style.width}`)
      }
    },
    setMapwarperLayers() {
      const currentMwLayers = {}
      this.mapwarperLayerDefs.forEach((mwDef) => {
        if (this.mapLayers.mapWarper[mwDef.id]) {
          currentMwLayers[mwDef.id] = this.mapLayers.mapWarper[mwDef.id]
        } else {
          currentMwLayers[mwDef.id] = {
            id: mwDef['mapwarper-id'],
            name: mwDef.title,
            active: (mwDef.active || 'false') === 'true',
            layer: this.$L.tileLayer(`https://mapwarper.net/maps/tile/${mwDef['mapwarper-id']}/{z}/{x}/{y}.png`)
          }
        }
      })
      for (const layerId in this.mapLayers.mapWarper) {
        if (!currentMwLayers[layerId]) {
          this.mapLayers.mapWarper[layerId].layer.removeFrom(this.map)
        }                
      }
      this.mapLayers.mapWarper = currentMwLayers
    },
    async setGeoJSONLayers() {
      const currentLayers = {}
      this.geojsonLayerDefs.forEach((def) => {
        if (this.mapLayers.geoJSON[def.id]) {
          currentLayers[def.id] = this.mapLayers.geoJSON[def.id]
        } else {
          currentLayers[def.id] = {
            id: def.id,
            name: def.title,
            active: (def.active || 'false') === 'true',
            layer: this.$L.geoJSON(
                  def.geojson,
                  { onEachFeature: this.onEachFeature }
                ).bindPopup(this.makePopup(def))
          }
        }
        this.featuresById[def.id] = currentLayers[def.id].layer
      })
      for (const layerId in this.mapLayers.geoJSON) {
        if (!currentLayers[layerId]) {
          this.mapLayers.geoJSON[layerId].layer.removeFrom(this.map)
        }                
      }
      this.mapLayers.geoJSON = currentLayers
    },
    setControls() {
      // let showOpacityControl = false
      const baseLayers = {
        base: this.mapLayers.baseLayer
      }
      const allLayers = {}
      const fadeableLayers = {}
      for (const layerId in this.mapLayers.geoJSON) {
        const layer = this.mapLayers.geoJSON[layerId]
        // fadeableLayers[layer.name] = this.mapLayers.geoJSON[layerId].layer
        allLayers[layer.name] = this.mapLayers.geoJSON[layerId].layer
      }
      for (const layerId in this.mapLayers.mapWarper) {
        const layer = this.mapLayers.mapWarper[layerId]
        fadeableLayers[layer.name] = this.mapLayers.mapWarper[layerId].layer
        allLayers[layer.name] = this.mapLayers.mapWarper[layerId].layer
        // console.log(`layer=${layer.name} active=${layer.active}`)
        // showOpacityControl = showOpacityControl || layer.active
      }
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
      // if (showOpacityControl) {
        this.controls.opacity =
            this.$L.control.opacity(
                fadeableLayers,
                {
                    // label: 'Layers Opacity',
                    collapsed: true 
                }
            ).addTo(this.map)
      // }
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
        this.setMapwarperLayers()
        this.setGeoJSONLayers()
        this.setMarkerGroups()
        this.sync()
      }
    },
    sync() {
      if (this.map) {
        for (const layerId in this.mapLayers.geoJSON) {
          const layer = this.mapLayers.geoJSON[layerId]
          if (layer.active) {
            this.map.addLayer(layer.layer)
          } else {
            this.map.removeLayer(layer.layer)
          }
        }
        for (const layerId in this.mapLayers.mapWarper) {
          const mwLayer = this.mapLayers.mapWarper[layerId]
          if (mwLayer.active) {
            this.map.addLayer(mwLayer.layer)
          } else {
            this.map.removeLayer(mwLayer.layer)
          }
        }
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
      console.log(item)
      return pu
    },
        /*
        this.layers.forEach((layer) => {
            const markerFeatures = layer.features.filter(feature => feature.type === 'marker')
            markerFeatures.forEach((feature) => {
                feature.leafletObject = this.$L.marker(feature.coords)
                .bindPopup(feature.name);
            })
            const polygonFeatures = layer.features.filter(feature => feature.type === 'polygon')
            polygonFeatures.forEach((feature) => {
                feature.leafletObject = this.$L.polygon(feature.coords)
                .bindPopup(feature.name);
            })
        })
        */
  },
  watch: {
    selectedItemID: {
      handler: function (value, prior) {
        //console.log(`Map.watch.selectedItemID=${this.selectedItemID}`, this.featuresById[this.selectedItemID])
        if (this.featuresById[this.selectedItemID]) {
          this.featuresById[this.selectedItemID].openPopup()
        }
      },
      immediate: true
    },
    viewport: {
      handler: function (value, prior) {
        this.positionMapContainer()
      },
      immediate: true
    },
    activeElements() {
      this.updateLayers()
    },
    mapsInActiveElements: {
      handler: function (value, prior) {
        // console.log('mapsInActiveElements', this.mapsInActiveElements.length)
        if (this.$refs.map) {
          if (this.mapsInActiveElements.length === 0) {
              this.$refs.mapWrapper.style.display = 'none'
          } else {
            if (this.map) {
              if (this.mapsInActiveElements.length > 0) {
                const curMap = this.mapsInActiveElements[this.mapsInActiveElements.length-1]
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
