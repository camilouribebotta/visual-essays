<template>
    <div ref="mapWrapper" class="row wrapper" style="width:100%; margin:0;">
        <div ref="mapWrapperInner">
            <div ref="map" id="lmap" class="lmap" style="margin:0;"></div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

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
    geojson: {},
    mapLayers: {
      baseLayer: null,
      mapwarper: {},
      markerGroups: {},
      geojson: {}
    },
    addedLayers: new Set(),
    controls: {},
    featuresById: {},
    markersByLatLng: {}
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
    loadGeojson(def) {
      console.log('loadGeojson', def.id, def.active)
      axios.get(def.url)
        .then(resp => {
          let geojson = L.geoJson(resp.data, {
            // Pop Up
            onEachFeature: function(feature, layer) {
              layer.bindPopup(`<p>${feature.properties.title}</p>`)
            },
            // Style
            style: function(feature) {
              return {
                  fillColor: feature.properties['fill'] || '#fff',
                  fillOpacity: feature.properties['fill-opacity'] || 0,
                  color: feature.properties['stroke'] || '#000',
                  width: feature.properties['stroke-width'] || 1,
                  opacity: feature.properties['opacity'] || 1
              }
            }
          })
          this.geojson[def.id] = geojson
          this.mapLayers.geojson[def.id] = {
            id: def.id,
            name: def.title,
            active: (def.active || 'false') === 'true',
            layer: geojson
          }
          this.addedLayers.add(def.id)
          geojson.addTo(this.map)
        })
    },
    syncGeojsonLayers() {
      Object.keys(this.mapLayers.geojson).forEach(cur => {
        if (this.addedLayers.has(cur) && !this.mapDef.layers.geojson.find(def => def.id === cur)) {
          console.log('remove geojson', cur)
          this.addedLayers.delete(cur)
          this.map.removeLayer(this.mapLayers.geojson[cur].layer)
        }
      })
      this.mapDef.layers.geojson.forEach(def => {
        if (!this.addedLayers.has(def.id)) {
          if (this.mapLayers.geojson[def.id]) {
            console.log('add geojson', def.id)
            this.addedLayers.add(def.id)
            this.mapLayers.geojson[def.id].layer.addTo(this.map)
          } else {
            this.loadGeojson(def)
          }
        }
      })
    },
    syncMapwarperLayers() {
      Object.keys(this.mapLayers.mapwarper).forEach(cur => {
        if (this.addedLayers.has(cur) && !this.mapDef.layers.mapwarper.find(def => def.id === cur)) {
          console.log('remove mapwarper', cur)
          this.addedLayers.delete(cur)
          this.map.removeLayer(this.mapLayers.mapwarper[cur].layer)
        }
      })
      this.mapDef.layers.mapwarper.forEach(def => {
        if (!this.addedLayers.has(def.id)) {
          if (this.mapLayers.mapwarper[def.id]) {
            console.log('add mapwarper', def.id)
            this.addedLayers.add(def.id)
            this.mapLayers.mapwarper[def.id].layer.addTo(this.map)
          } else {
            const layer = this.$L.tileLayer(`https://mapwarper.net/maps/tile/${def['mapwarper-id']}/{z}/{x}/{y}.png`)
            this.mapLayers.mapwarper[def.id] = {
              id: def.id,
              name: def.title,
              active: (def.active || 'false') === 'true',
              layer
            }
            layer.addTo(this.map)
          }
        }
      })
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
          if (layer) {
            allLayers[layer.name] = layer.layer
            if (layerType === 'mapwarper') {
              fadeableLayers[layer.name] = layer.layer
            }
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
        const marker = this.$L.marker(location.coords[0])
        // .bindPopup(this.makePopup(location))
        marker.addEventListener('click', (e) => {
          const elemId = this.markersByLatLng[`${e.latlng.lat},${e.latlng.lng}`]
          this.$store.dispatch('setSelectedItemID', elemId)
        })   
        markers.push(marker)
        const mll = marker.getLatLng()
        this.featuresById[location.id] = marker
        this.markersByLatLng[`${mll.lat},${mll.lng}`] = location.id
      })
      return markers
    },
    syncMarkerGroups() {
      for (const groupName in this.mapLayers.markerGroups) {
        const markerGroup = this.mapLayers.markerGroups[groupName]
        this.map.removeLayer(markerGroup.layer)
      }
      const currentMarkerGroups = {}
      
      const layer = this.$L.layerGroup([...this.getLocationMarkers()])
      currentMarkerGroups['locations'] = {
        name: 'Locations',
        active: true,
        layer
      }
      layer.addTo(this.map)

      this.mapLayers.markerGroups = currentMarkerGroups
    },
    updateLayers() {
      if (this.map) {
        this.syncGeojsonLayers()
        this.syncMapwarperLayers()
        this.syncMarkerGroups()
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
        this.positionMapContainer()
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
        /* fill-opacity: 1; */
    }

    .leaflet-container {
        background: #aad3df;
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
           cover = fills entire box, maintains asp dect ration, clipped to fit
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

    .leaflet-bar a, .leaflet-bar a:hover {
        height: 30px;
        width: 36px;
    }
    
    .leaflet-right .leaflet-control {
        float: left;
    }

    .leaflet-top.leaflet-left {
        top: 6px;
        left: 6px;
    }

    .leaflet-top.leaflet-right {
        left: 16px;
        top: 90px;
        right: unset;
    }


  

</style>
