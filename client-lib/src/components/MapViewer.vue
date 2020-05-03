<template>
    <div ref="mapWrapper" class="row wrapper" style="width:100%; margin:0;">
        <div ref="mapWrapperInner">
            <div ref="map" id="lmap" class="lmap" style="margin:0;"></div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

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
  zoom: 2.5
}

const iconMap = {
  garden: 'leaf'
}

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
    locations() { return this.itemsInActiveElements.filter(entity => entity.coords || entity.geojson) },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
  },
  mounted() {
    this.$nextTick(() => { this.createBaseMap() })
  },
  methods: {
    createBaseMap() {
      this.positionMapContainer()
      console.log(`createBaseMap: basemap=${this.mapDef.basemap} title=${this.mapDef.title} center=${this.mapDef.center} zoom=${this.mapDef.zoom}`)  
      this.map = this.$L.map('lmap', {center: this.mapDef.center || defaults.center, zoom: this.mapDef.zoom || defaults.zoom, zoomSnap: 0.1})
      this.mapLayers.baseLayer = this.$L.tileLayer(...baseLayers[this.mapDef.basemap || defaults.basemap])
      this.map.addLayer(this.mapLayers.baseLayer)

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
        // console.log(`wrapperWidth=${wrapperWidth} calculatedContainerHeight=${calculatedContainerHeight} mapHeight=${mapHeight} mapWidth=${mapWidth}`)
        // center the map
        this.$refs.mapWrapperInner.style.paddingTop = 0
        this.$refs.mapWrapperInner.style.paddingBottom = 0
        this.$refs.mapWrapperInner.style.paddingLeft = `${(wrapperWidth - mapWidth)/2}px`
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
      console.log('loadGeojson', def.url || def.geojson, `cached=${this.$store.getters.geoJsonCache[def.id] !== undefined}`)
      if (!this.$store.getters.geoJsonCache[def.id]) {
        const cacheObj = {}
        cacheObj[def.id] = axios.get(def.url || def.geojson)
        this.$store.dispatch('addToGeoJsonCache', cacheObj)
      }
      return this.$store.getters.geoJsonCache[def.id]
    },
    loadGeojson(def) {
      this.cachedGeojson(def)
      .then(resp => {
        const self = this
        let numFeatureLabels = 0
        let geojson = L.geoJson(resp.data, {
          // Pop Up
          onEachFeature: function(feature, layer) {
            //layer.bindPopup('layer', { autoClose: false, closeButton: false, closeOnClick: false })
            // layer.addEventListener('click', (e) => console.log('geojson.layer clicked'))
            if (!def.title) {
              const label = feature.properties ? feature.properties.label || feature.properties.name || feature.properties.title || undefined : undefined
              if (label) {
                layer.addEventListener('click', (e) => console.log('geojson.feature clicked', feature))
                feature.properties.label = label
                layer.bindPopup(self.makePopup(label), { autoClose: true, closeButton: false, closeOnClick: true })
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
              ? geojson.properties.label || geojson.properties.name || geojson.properties.title || undefined
              : undefined
          if (label) {
            geojson.bindPopup(self.makePopup(label), { autoClose: false, closeButton: false, closeOnClick: false })
            console.log(this.mapDef)
            if (this.mapDef['hide-labels'] !== 'true') {
              const t = performance.now()
              geojson.openPopup()
              console.log('open geojson popup', Math.round(performance.now() - t), label)
            }
          }
        }

        this.addedLayers.add(def.id)
        if (this.mapDef['hide-labels'] !== 'true') {
          const t = performance.now()
          geojson.eachLayer(feature => {feature.openPopup(); console.log(feature.properties)})
          console.log('open geojson feature popup', Math.round(performance.now() - t))
        }
        // this.map.setView(this.mapDef.center || defaults.center, this.mapDef.zoom || defaults.zoom)
        console.log('flyTo', this.mapDef.center || defaults.center)
        this.map.flyTo(this.mapDef.center || defaults.center, this.mapDef.zoom || defaults.zoom)

        return geojson
      })
    },
    syncGeojsonLayers() {
      const layers = []
      let start = performance.now()
      Object.keys(this.mapLayers.geojson).forEach(cur => {
        if (this.addedLayers.has(cur) && !this.mapDef.layers.geojson.find(def => def.id === cur)) {
          this.addedLayers.delete(cur)
          this.map.removeLayer(this.mapLayers.geojson[cur].layer)
        }
      })
      start = performance.now()
      this.mapDef.layers.geojson.forEach(def => {
        if (!this.addedLayers.has(def.id)) {
          if (this.mapLayers.geojson[def.id]) {
            this.addedLayers.add(def.id)
            const geojson = this.mapLayers.geojson[def.id].layer
            geojson.addTo(this.map)
            if (this.mapDef['hide-labels'] !== 'true') {
              const t = performance.now()
              geojson.eachLayer(feature => {feature.openPopup(); console.log(feature)})                      
              console.log('open added geojson popup', Math.round(performance.now() - t))
            }
          } else {
            layers.push(this.loadGeojson(def))
            // console.log(performance.now() - s1)
          }
        }
      })
      //console.log('add geojson', performance.now() - start)
      this.locations.filter(location => location.geojson && location['prefer-geojson'] && location['prefer-geojson'].toLowerCase() === 'true').forEach(location => {
        if (!this.addedLayers.has(location.id)) {
          if (this.mapLayers.geojson[location.id]) {
            this.addedLayers.add(location.id)
            const geojson = this.mapLayers.geojson[location.id].layer
            geojson.addTo(this.map)
            if (this.mapDef['hide-labels'] !== 'true') {
              const t = performance.now()
              geojson.eachLayer(feature => {feature.openPopup(); console.log(feature)})
              console.log('open added geojson location popup', Math.round(performance.now() - t)) 
            }
          } else {
            this.loadGeojson(location)
          }
        }
      })
     return layers
    },
    getLocationMarkers() {
      const markers = []
      // this.locations.filter(location => location.coords && !location.geojson).forEach((location) => {
      this.locations.filter(location => location.coords && !(location.geojson !== undefined && location['prefer-geojson'] && location['prefer-geojson'].toLowerCase() === 'true')).forEach((location) => {
        const marker = this.makeMarker(location.coords[0], location)
        marker.addEventListener('click', (e) => {
          const elemId = this.markersByLatLng[`${e.latlng.lat},${e.latlng.lng}`]
          this.$store.dispatch('setSelectedItemID', elemId)
        })
        if (location.title || location.label) {
          marker.bindPopup(this.makePopup(location.title || location.label), { autoClose: false, closeButton: false, closeOnClick: false })
        }
        markers.push(marker)
        const mll = marker.getLatLng()
        this.featuresById[location.id] = marker
        this.markersByLatLng[`${mll.lat},${mll.lng}`] = location.id
      })
      return markers
    },
    syncMapwarperLayers() {
      Object.keys(this.mapLayers.mapwarper).forEach(cur => {
        if (this.addedLayers.has(cur) && !this.mapDef.layers.mapwarper.find(def => def.id === cur)) {
          this.addedLayers.delete(cur)
          this.map.removeLayer(this.mapLayers.mapwarper[cur].layer)
        }
      })
      this.mapDef.layers.mapwarper.forEach(def => {
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
      // console.log(`open marker popup: hide-labels=${this.mapDef['hide-labels']} show=${this.mapDef['hide-labels'] !== 'true'}`)
      if (this.mapDef['hide-labels'] !== 'true') {
        markers.forEach(marker => {
          var t = performance.now()
          marker.openPopup()
          console.log('open marker popup', Math.round(performance.now() - t), marker._popup._content)
        })
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
        // console.log('selected', this.selected)
        //if (this.featuresById[this.selected]) {
        //  this.featuresById[this.selected].openPopup()
        //}
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
                console.log('flyto', this.mapDef.center || defaults.center)
                this.map.flyTo(this.mapDef.center || defaults.center, this.mapDef.zoom || defaults.zoom)
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
        margin-bottom: 0;
        font-size: 12px;
        font-weight: 500;
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
