<template>
  <div id="mapWrapper" ref="mapWrapper" class="row wrapper">
       <div ref="map" id="lmap" class="lmap" :style="`width:${width}px; height:${Math.min(viewport.height, height)}px; margin:0;`"></div>
  </div>
</template>

<script>

const baseLayers = {
  'OpenStreetMap': ['https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        { maxZoom: 18, attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' }],
  'Esri_WorldPhysical': ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}', 
        { maxZoom: 8, attribution: 'Tiles &copy; Esri &mdash; Source: US National Park Service' }],
  'OpenTopoMap': ['https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        { maxZoom: 17, attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)' }],
  'Stamen_Watercolor': ['https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}',
        {	subdomains: 'abcd', minZoom: 1, maxZoom: 16, ext: 'jpg', attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }]
}

const defaults = {
  basemap: 'OpenStreetMap',
  center: [25, 0],
  zoom: 2.5,
  popupOptions: { autoClose: false, closeButton: false, closeOnClick: false }
}

const iconMap = {
  garden: 'leaf'
}

module.exports = {
  name: 'MapViewer',
  props: {
    items: Array,
    selected: String,
    width: Number,
    height: Number
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
    entities() { return this.itemsInActiveElements.filter(item => item.tag === 'entity') },
    locations() { return this.itemsInActiveElements.filter(entity => entity.coords || entity.geojson) },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
    isHorizontal() { return this.$store.getters.layout[0] === 'h' },
    isSelected() { return this.selected === 'map' },
    // width() { return Math.min(this.viewport.width, this.viewerWidth)},
  },
  mounted() {
    // console.log(`MapViewer.mounted: height=${this.height} width=${this.width}`)
    this.$nextTick(() => { this.createBaseMap() })
  },
  methods: {
    createBaseMap() {
      const t = performance.now()
      if (this.map) {
        this.map.off()
        this.map.remove()
        this.map = undefined
        this.addedLayers = new Set()
      }
      if (!this.map) {
        this.mapLayers.baseLayer = this.$L.tileLayer(...baseLayers[this.mapDef.basemap || defaults.basemap])
        this.map = this.$L.map('lmap', {
          preferCanvas: true,
          center: this.mapDef.center || defaults.center, 
          zoom: this.mapDef.zoom || defaults.zoom, zoomSnap: 0.1,
          layers: [this.mapLayers.baseLayer]})
        console.log(`createBaseMap: basemap=${this.mapDef.basemap} title=${this.mapDef.title} center=${this.mapDef.center} zoom=${this.mapDef.zoom} elapsed=${Math.round(performance.now() - t)}`)
        this.updateLayers()
      }
    },
    makeMarker(latlng, props) {
      const faIcon = iconMap[props['marker-symbol']] || props['marker-symbol'] || 'circle'
      return L.marker(latlng, {
        icon: L.icon.fontAwesome({
          iconClasses: `fa fa-${faIcon}`, // you _could_ add other icon classes, not tested.
          markerColor: props['marker-color'] || props['fill'] || '#2C84CB',
          markerFillOpacity: props['opacity'] || 1,
          markerStrokeColor: props['stroke'] || props['marker-color']|| props['fill'] || '#2C84CB',
          markerStrokeWidth: props['stroke-width'] || 0,
          iconColor: props['marker-symbol-color'] || '#FFF',
          iconXOffset: props['marker-symbol-xoffset'] || 0,
          iconYOffset: props['marker-symbol-yoffset'] || 0
        })
      })
    },
    makePopup(label) {
      let popup = `<h1>${label}</h1>`
      /*
      if (props.images) {
        popup += `<img src="${props.images[0]}">`
        popup = `<div style="width: 125px !important; height:135px !important;">${popup}</div>`
      }
      */
      return popup
    },
    cachedGeojson(def) {
      // console.log('loadGeojson', def.url || def.geojson, `cached=${this.$store.getters.geoJsonCache[def.id] !== undefined}`)
      if (!this.$store.getters.geoJsonCache[def.id]) {
        const cacheObj = {}
        cacheObj[def.id] = fetch(def.url || def.geojson).then(resp => resp.json())
        this.$store.dispatch('addToGeoJsonCache', cacheObj)
      }
      return this.$store.getters.geoJsonCache[def.id]
    },
    loadGeojson(def) {
      this.cachedGeojson(def)
      .then(data => {
        const self = this
        let numFeatureLabels = 0
        let geojson = L.geoJson(data, {
          // Pop Up
          onEachFeature: function(feature, layer) {
            // layer.addEventListener('click', (e) => console.log('geojson.layer clicked'))
            if (!def.title) {
              const label = feature.properties ? feature.properties.label || feature.properties.name || feature.properties.title || feature.properties['ne:NAME'] || undefined : undefined
              if (label) {
                // layer.addEventListener('click', (e) => console.log('geojson.feature clicked', feature))
                feature.properties.label = label
                layer.bindPopup(self.makePopup(label), defaults.popupOptions )
                numFeatureLabels += 1
              }
            }
            if (feature.properties.decorators) {
              const polyline = self.$L.polyline(self.$L.GeoJSON.coordsToLatLngs(feature.geometry.coordinates), {})
              const patterns = []
              feature.properties.decorators.forEach(decoratorProps => {
                // console.log('decorator', decoratorProps)
                if (decoratorProps.symbol === 'arrow') {
                  patterns.push(decoratorProps)
                  decoratorProps.symbol = self.$L.Symbol.arrowHead({
                    pixelSize: 15,
                    polygon: false,
                    pathOptions: {
                      stroke: true,
                      width: feature.properties['stroke-width'] || 4,
                      color: feature.properties.stroke || '#FB683F'
                    }
                  })
                }
                const decorator = self.$L.polylineDecorator(polyline, {patterns}).addTo(self.map)
              })
            }
          },
          // Style
          style: function(feature) {
            return {
                color: feature.properties['stroke'] || '#FB683F',
                weight: feature.properties['stroke-width'] || 4,
                opacity: feature.properties['stroke-opacity'] || 1,                  
                fillColor: feature.properties['fill'] || '#32C125',
                fillOpacity: feature.properties['fill-opacity'] || 0.5,
            }
          },
          pointToLayer: function(feature, latlng) {
            return self.makeMarker(latlng, feature.properties)
          }
        }).addTo(this.map)

        this.geojson[def.id] = geojson
        this.mapLayers.geojson[def.id] = {
          id: def.id,
          name: def.title,
          active: (def.active || 'false') === 'true',
          layer: geojson
        }
       
        if (numFeatureLabels === 0) {
          const label = def.title
            ? def.title
            : geojson.properties
              ? geojson.properties.label || geojson.properties.name || geojson.properties.title || geojson.properties['ne:NAME'] || undefined
              : undefined
          if (label) {
            geojson.bindPopup(self.makePopup(label), defaults.popupOptions)
            if (this.showLabels()) {
              geojson.openPopup()
            }
          }
        }

        this.addedLayers.add(def.id)
        if (this.showLabels()) {
          geojson.eachLayer(feature => feature.openPopup())
        }
        this.map.flyTo(this.mapDef.center || defaults.center, this.mapDef.zoom || defaults.zoom)

        return geojson
      })
    },
    syncGeojsonLayers() {
      let t = performance.now()
      const layers = []
      Object.keys(this.mapLayers).filter(layer => layer.url).forEach(cur => {
        if (this.addedLayers.has(cur) && !this.mapDef.layers.find(def => def.id === cur)) {
          this.addedLayers.delete(cur)
          this.map.removeLayer(this.mapLayers.geojson[cur].layer)
        }
      })

      this.mapDef.layers.filter(layer => layer.url).forEach(def => {
        if (!this.addedLayers.has(def.id)) {
          if (this.mapLayers.geojson[def.id]) {
            this.addedLayers.add(def.id)
            const geojson = this.mapLayers.geojson[def.id].layer
            geojson.addTo(this.map)
            if (this.showLabels()) {
              geojson.openPopup()
              geojson.eachLayer(feature => feature.openPopup())                      
            }
          } else {
            layers.push(this.loadGeojson(def))
          }
        }
      })

      this.locations.filter(location => this.useGeojson(location)).forEach(location => {
        if (!this.addedLayers.has(location.id)) {
          if (this.mapLayers.geojson[location.id]) {
            this.addedLayers.add(location.id)
            const geojson = this.mapLayers.geojson[location.id].layer
            this.map.addLayer(geojson)
            if (this.showLabels()) {
              geojson.openPopup()
              geojson.eachLayer(feature => feature.openPopup())
            }
          } else {
            this.loadGeojson(location)
          }
        }
      })
      console.log(`syncGeojsonLayers: elapsed=${Math.round(performance.now() - t)}`)
      return layers
    },
    useGeojson(location) {
      let useGeojson = false
      if (location.geojson) {
        let preferAttr = location['prefer-geojson'] || this.mapDef['prefer-geojson']
        if (preferAttr !== undefined) {
          preferAttr = preferAttr.toLowerCase()
          useGeojson = preferAttr === '' || preferAttr === 'true'
        }
      }
      return useGeojson
    },
    showLabels() {
      return !(this.mapDef['hide-labels'] === '' || this.mapDef['hide-labels'] === 'true')
    },
    getLocationMarkers() {
      const markers = []
      // this.locations.filter(location => location.coords && !location.geojson).forEach((location) => {
      this.locations.filter(location => location.coords && !this.useGeojson(location)).forEach((location) => {
        const marker = this.makeMarker(location.coords[0], location)
        marker.addEventListener('click', (e) => {
          const elemId = this.markersByLatLng[`${e.latlng.lat},${e.latlng.lng}`]
          this.$store.dispatch('setSelectedItemID', elemId)
        })
        if (location.title || location.label) {
          marker.bindPopup(this.makePopup(location.title || location.label), defaults.popupOptions)
        }
        markers.push(marker)
        const mll = marker.getLatLng()
        this.featuresById[location.id] = marker
        this.markersByLatLng[`${mll.lat},${mll.lng}`] = location.id
      })
      return markers
    },
    syncMapwarperLayers() {
      Object.keys(this.mapLayers).filter(layer => layer['mapwarper-id']).forEach(cur => {
        if (this.addedLayers.has(cur) && !this.mapDef.layers.find(def => def.id === cur)) {
          this.addedLayers.delete(cur)
          this.map.removeLayer(this.mapLayers.mapwarper[cur].layer)
        }
      })
      this.mapDef.layers.filter(layer => layer['mapwarper-id']).forEach(def => {
        if (!this.addedLayers.has(def.id)) {
          let layer
          if (this.mapLayers.mapwarper[def.id]) {
            this.addedLayers.add(def.id)
            layer = this.mapLayers.mapwarper[def.id].layer
          } else {
            layer = this.$L.tileLayer(`https://mapwarper.net/maps/tile/${def['mapwarper-id']}/{z}/{x}/{y}.png`)
            this.mapLayers.mapwarper[def.id] = {
              id: def.id,
              name: def.title,
              active: (def.active || 'false') === 'true',
              layer
            }
          }
          if (this.mapLayers.mapwarper[def.id].active) {
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
      this.mapDef.layers.forEach(layerDef => {
        const layerType = layerDef.url ? 'geojson' : 'mapwarper'
        const layer = this.mapLayers[layerType][layerDef.id]
        if (layer) {
          allLayers[layer.name] = layer.layer
          if (layerType === 'mapwarper') {
            fadeableLayers[layer.name] = layer.layer
          }
        }
      })
      /*
      for (const layerId in this.mapLayers.markerGroups) {
        const layer = this.mapLayers.markerGroups[layerId]
        allLayers[layer.name] = this.mapLayers.markerGroups[layerId].layer
      }
      */

      if (this.controls.layers) {
        this.map.removeControl(this.controls.layers)
      }
      if (Object.keys(allLayers).length > 0) {
        this.controls.layers =
          this.$L.control.layers(
            {}, // baseLayers,
            allLayers, 
            { collapsed: true } //options
          ).addTo(this.map)
      }
      // opacity control
      if (this.controls.opacity) {
        this.map.removeControl(this.controls.opacity)
      }
      if (Object.keys(fadeableLayers).length > 0) {
        this.controls.opacity =
            this.$L.control.opacity(
                fadeableLayers,
                {
                  // label: 'Layers Opacity',
                  collapsed: true
                }
            ).addTo(this.map)
      }
    },
    syncMarkerGroups() {
      for (const groupName in this.mapLayers.markerGroups) {
        const markerGroup = this.mapLayers.markerGroups[groupName]
        this.map.removeLayer(markerGroup.layer)
      }
      const currentMarkerGroups = {}
      
      const markers = [...this.getLocationMarkers()]
      const layer = this.$L.layerGroup(markers)
      currentMarkerGroups['locations'] = {
        name: 'Locations',
        active: true,
        layer
      }
      layer.addTo(this.map)
      if (this.showLabels()) {
        markers.forEach(marker => marker.openPopup())
      }
      this.mapLayers.markerGroups = currentMarkerGroups
    },
    updateLayers() {
      if (this.map) {
        this.syncGeojsonLayers()
        this.syncMapwarperLayers()
        this.syncMarkerGroups()
        this.setControls()
      }
    }
  },
  watch: {
    selected: {
      handler: function (value, prior) {
        const map = document.getElementById('map')
        if (this.isSelected && map && map.style.display === 'none') {
          map.style.display = 'block'
        }
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
      handler: function (mapDef, prior) {
        console.log('mapDef', this.mapDef)
        const lmap = document.getElementById('lmap')
        if (lmap) {
          if (mapDef) {
            if (this.map && mapDef && !prior || mapDef.basemap === prior.basemap) {
              this.map.flyTo(mapDef.center || defaults.center, mapDef.zoom || defaults.zoom)
            } else {
              this.createBaseMap()
            }
            this.$refs.mapWrapper.style.display = 'block'
          } else {
            this.$refs.mapWrapper.style.display = 'none'
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
  }

  .leaflet-interactive {
    /* fill-opacity: 1; */
  }

  .leaflet-container {
      background: #aad3df !important;
  }

  .leaflet-popup-content {
      margin: 5px 8px !important;
      line-height: 1 !important;
  }

  .leaflet-popup-content-wrapper {
      border-radius: 4px !important;
  }

  .leaflet-popup-content-wrapper, .leaflet-popup-tip {
      color: black !important;
      box-shadow: 0 2px 4px rgb(0,0,0,0.5) !important;
  }

  .leaflet-popup-content-wrapper h1 {
    max-width: 120px;
    line-height: 1.2;
    margin: 0;
    font-size: 12px;
    font-weight: 500;
    text-align: center;
    display: inherit;
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
        height: 30px !important;
        width: 36px !important;
    }
    
    .leaflet-right .leaflet-control {
        float: left;
    }

    .leaflet-top.leaflet-left {
        top: 6px;
        right: 16px;
        left: unset;
    }

    .leaflet-top.leaflet-right {
        left: unset;
        top: 90px;
        right: 6px;
    }

  .leaflet-fa-markers {
    position: absolute;
    left: 0;
    top: 0;
    display: block;
    text-align: center;
    margin-left: -15px;
    margin-top: -50px;
    width: 160px;
    height: 50px;
  }

  .leaflet-fa-markers .marker-icon-svg {
    position: absolute;
  }

  .leaflet-fa-markers .feature-icon {
    position: absolute;
    font-size: 14px;
    line-height: 0px;
    left: 8px;
    top: 10px;
    display: inline-block;
  }

</style>
