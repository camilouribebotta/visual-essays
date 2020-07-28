<template>
  <div id="mapWrapper" ref="mapWrapper" class="row wrapper">
    <div ref="map" id="lmap" class="lmap" :style="`width:${width}px; height:${mapHeight}px; margin:0;`"></div>
    <div ref="timeSelector" v-if="timeSelector" style="height: 45px; padding: 0 24px;">
      <time-selector :initial-time-range="timeRange" @range-change="rangeChange" :data="timeData" />
    </div>
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
    height: Number,
    hoverItemID: String,
    selectedItemID: String
  },
  data: () => ({
    map: null,
    // geojson: {},
    baseLayer: undefined,
    layers: {},
    layersControl: undefined,
    opacityControl: undefined,
    popups: {},
    active: new Set(),
    featuresById: {},
    markersByLatLng: {},
    mapHeight: 0,

    geojsonIsLoading: false,
    dateField: 'date',
    data: [],
    timeData: [],
    timeRange: [],
    min: undefined,
    max: undefined
  }),
  computed: {
    mapDef() { return this.items[0] },
    timeSelector() { return this.mapDef['time-selector'] },
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
    console.log(`MapViewer.mounted: height=${this.height} width=${this.width}`)
    this.mapHeight = this.height
    this.$nextTick(() => this.createBaseMap())
  },
  methods: {
    rangeChange(range) {
      this.timeRange = range
      this.map.removeLayer(this.layers.Labels)
      this.map.eachLayer(layer => {
        if (layer.options.type === 'geojson' && layer.options.id && layer.options.id.indexOf('map-layer-1') === 0) {
          this.map.removeLayer(layer)
        }
      })
      this.syncLayers()
    },
    timeRangeFilter(feature) {
      console.log(this.timeRange)
      if (feature.properties[this.dateField]) {
        const dateStrs = feature.properties[this.dateField].split(':')
        feature.properties.startDate = this.parseDate(dateStrs[0]).getUTCFullYear()
        feature.properties.endDate = dateStrs.length === 1 ? feature.properties.startDate : this.parseDate(dateStrs[1]).getUTCFullYear()
        feature.properties.value = feature.properties.startDate
        this.data.push(feature.properties)
      }
      if (feature.properties.startDate && this.timeRange.length === 2) {
        return feature.properties.startDate >= this.timeRange[0] && feature.properties.endDate <= this.timeRange[1]
      }
      return true
    },
    createBaseMap() {
      const t = performance.now()
      if (this.map) {
        this.map.off()
        this.map.remove()
        this.map = undefined
      }
      if (!this.map) {
        if (this.timeSelector) {
          if (this.timeSelector !== 'true') {
            const initialRangeDates = this.timeSelector.split(':').map(dateStr => this.parseDate(dateStr).getUTCFullYear())
            this.timeRange = initialRangeDates.length === 2 ? initialRangeDates : [initialRangeDates[0], initialRangeDates[0]]
          }
        }
        this.$nextTick(() => {
          const timeSelectorHeight = this.$refs.timeSelector ? this.$refs.timeSelector.clientHeight : 0
          const basemap = this.mapDef.basemap || defaults.basemap
          const center = this.mapDef.center || defaults.center
          const zoom = this.mapDef.zoom || defaults.zoom
          this.baseLayer = this.$L.tileLayer(...baseLayers[basemap])
          this.map = this.$L.map('lmap', {
            preferCanvas: true,
            center, zoom, zoomSnap: 0.1,
            layers: [this.baseLayer]})
          console.log(`createBaseMap: height=${this.height} width=${this.width} timeSelector=${this.timeSelector !== undefined} basemap=${basemap} title=${this.mapDef.title} center=${center} zoom=${zoom} elapsed=${Math.round(performance.now() - t)}`)
          this.updateLayers()
        })
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
          iconYOffset: props['marker-symbol-yoffset'] || 0,
        }),
        id: props.eid
      })
    },
    setHoverItemID(itemID) {
      this.$emit('hover-id', itemID)
    },
    setSelectedItemID(itemID) {
      this.$emit('selected-id', itemID)
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
    addEventHandlers(elem, itemId) {
      elem.on('click', () => { this.setSelectedItemID(itemId) })
      elem.on('mouseover', () => { this.setHoverItemID(itemId) })
      elem.on('mouseout', () => { this.setHoverItemID() })
    },
    addPopup(id, label, latLng, offset) {
      if (!this.popups[id]) {
        // console.log(`addPopup: id=${id} label=${label} lagLng=${latLng} offset=${offset}`)
        const popup = L.popup({ ...defaults.popupOptions, ...{ offset: L.point(0, offset || 0)}})
        popup.setLatLng(latLng)
        popup.setContent(`<h1 data-eid="${id}">${label}</h1>`)
        popup.options.id = id
        this.popups[id] = popup
      }
    },
    loadGeojson(def, addToMap) {
      this.geojsonIsLoading = true
      this.dateField = def['date-field'] || this.dateField
      this.cachedGeojson(def)
      .then(data => {
        const self = this
        let numFeatureLabels = 0
        console.log('loadGeojson')
        let geojson = L.geoJson(data, {
          filter: this.timeRangeFilter,
          onEachFeature: function(feature, layer) {
            layer.options.id = def.id
            feature.properties.layerid = def.id
            const latLng = layer.feature.geometry.type === 'Polygon' || layer.feature.geometry.type === 'MultiPolygon' || layer.feature.geometry.type === 'LineString'
              ? layer.getBounds().getCenter()
              : layer.getLatLng()
            feature.properties.id = feature.properties.id || `${latLng}`
            // console.log(`feature: id=${feature.properties.id} layerid=${feature.properties.layerid}`)
            self.addEventHandlers(layer, layer.feature.properties.id)
            //if (!def.title) {
              const label = feature.properties ? feature.properties.label || feature.properties.name || feature.properties.title || feature.properties['ne:NAME'] || undefined : undefined
              if (label) {
                numFeatureLabels += 1
                feature.properties.label = label
                self.addPopup(feature.properties.id, label, latLng, feature.geometry.type === 'Point' ? -20 : 0)
                self.addEventHandlers(layer, layer.feature.properties.id)
                self.active.add(feature.properties.id)
                /*
                const _layers = { ...self.layers, ...{ Labels: self.$L.layerGroup(Object.values(self.popups).filter(popup => self.active.has(layerId))) } }
                if (!(self.mapDef['hide-labels'] === '' || self.mapDef['hide-labels'] === 'true')) {
                  _layers.Labels.addTo(self.map)
                }
                this.layers = _layers
                */
              }
            //}
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
                      width: parseFloat(feature.properties['stroke-width']) || 4,
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
            for (let [prop, value] of Object.entries(feature.properties)) {
              if (value === 'null') {
                feature.properties[prop] = null
              }
            }
            const style = {
                color: def['stroke'] || feature.properties['stroke'] || '#FB683F',
                weight: parseFloat(def['stroke-width'] || feature.properties['stroke-width'] || (feature.geometry.type === 'Polygon' || feature.geometry.type === 'MultiPolygon' ? 0 : 4)),
                opacity: parseFloat(def['stroke-opacity'] || feature.properties['stroke-opacity'] || 1),                  
                fillColor: def['fill'] || feature.properties['fill'] || '#32C125',
                fillOpacity: parseFloat(def['fill-opacity'] || feature.properties['fill-opacity'] || 0.5),
            }
            return style
          },
          //pointToLayer: function(feature, latlng) {
          //  return self.makeMarker(latlng, feature.properties)
          //}
        })

        const geojsonLabel = def.title
          ? def.title
          : data.properties
            ? data.properties.label || data.properties.name || data.properties.title || data.properties['ne:NAME'] || data.properties['ne:name'] || undefined
            : undefined

        geojson.options.id = def.id

        if (addToMap || def.active) {
          const currentLayers = new Set()
          this.map.eachLayer(layer => {if (layer.options.id) currentLayers.add(layer.options.id)})
          // this.map.eachLayer(layer => console.log('layer', layer.options.id))
          //if (!currentLayers.has(geojson.options.id)) {
            // console.log('adding geojson.layer', geojson.options.id)
            geojson.addTo(this.map)
          //}
        }

        if (numFeatureLabels === 0) {
          const latLng = geojson.getBounds().getCenter()
          this.addPopup(`${latLng}`, geojsonLabel, latLng)
          this.addEventHandlers(geojson, def.id)
        }

        geojson.options.id = def.id
        geojson.options.label = geojsonLabel
        geojson.options.type = 'geojson'

        const _layers = { 
          ...this.layers, 
          ...{ Labels: this.$L.layerGroup(Object.values(this.popups).filter(popup => this.active.has(popup.options.id))) } 
        }
        if (!(this.mapDef['hide-labels'] === '' || this.mapDef['hide-labels'] === 'true')) {
          _layers.Labels.addTo(this.map)
        }
        _layers[geojsonLabel] = geojson
        this.layers = _layers

        this.map.flyTo(this.mapDef.center || defaults.center, this.mapDef.zoom || defaults.zoom)
        
        this.geojsonIsLoading = false

        return geojson
      })
    },

    useGeojson(location) {
      return location.geojson && (!location.coords || location['prefer-geojson'] === 'true' || this.mapDef['prefer-geojson'] === 'true')
    },

    getLocationMarkers() {
      const markers = []
      this.locations.filter(location => location.coords && !this.useGeojson(location)).forEach((location) => {
        const marker = this.makeMarker(location.coords[0], location)
        const markerLabel = location.title || location.label
        const latLng = marker.getLatLng()
        this.addPopup(`${latLng}`, markerLabel, latLng, -45)
        this.addEventHandlers(marker, location.eid)
        markers.push(marker)
        const mll = marker.getLatLng()
        this.featuresById[location.id] = marker
        this.markersByLatLng[`${mll.lat},${mll.lng}`] = location.id
      })
      return markers
    },

    syncLayers() {
      const currentLayerIds = new Set(this.mapDef.layers.map(def => def.id))
      const _layers = {}
      const _active = new Set()

      this.map.eachLayer(layer => {
        if (layer !== this.baseLayer) {
          if (layer.options.id) {
            if (currentLayerIds.has(layer.options.id)) {
              _layers[layer.options.label] = layer
              _active.add(layer.options.id)
            } else {
              this.map.removeLayer(layer)
            }
          }
        }
      })

      this.mapDef.layers.forEach(layerDef => {
        let layer
        const layerLabel = layerDef.title || layerDef.id
        if (!_layers[layerLabel]) {
          if (layerDef.type === 'geojson') {
            _active.add(layerDef.id)
            this.loadGeojson(layerDef)
          } else if (layerDef.type === 'mapwarper') {
            layer = this.$L.tileLayer(`https://mapwarper.net/maps/tile/${layerDef['mapwarper-id']}/{z}/{x}/{y}.png`)
            layer.options.id = layerDef.id
            layer.options.label = layerLabel
            layer.options.type = 'mapwarper'
            _layers[layerLabel] = layer
            if (layerDef.active) {
              layer.addTo(this.map)
            }
          }
        }
      })

      this.locations.filter(location => this.useGeojson(location)).forEach(location => {
        _active.add(location.id)
        this.loadGeojson(location, true)
      })

      const markers = [...this.getLocationMarkers()]
      if (markers.length > 0) {
        const layer = this.$L.layerGroup(markers)
        layer.options.id = 'markers'
        layer.options.label = 'Locations'
        layer.options.type = 'markers'
        layer.addTo(this.map)
        _layers.Locations = layer
        markers.forEach(marker => _active.add(marker.options.id))
      }
      
      _layers.Labels = this.$L.layerGroup(Object.values(this.popups).filter(popup => _active.has(popup.options.id)))
      if (!(this.mapDef['hide-labels'] === '' || this.mapDef['hide-labels'] === 'true')) {
       _layers.Labels.addTo(this.map)
      }
      this.layers = _layers

      this.active = _active
    },
    updateLayers() {
      if (this.map) {
        this.syncLayers()
      }
    },
    mapChanged(current, prior) {
      return false
      // return !prior || current.basemap !== prior.basemap || current['time-selector'] !== prior['time-selector']
    }
  },
  watch: {
    geojsonIsLoading: {
      handler: function (isLoading, prior) {
        if (isLoading) {
          this.data = []
        } else {
          this.timeData = this.data
        }
      },
      immediate: false
    },
    hoverItemID: {
      handler: function (itemID, prior) {
        // console.log(`hoverItemID: value=${itemID} prior=${prior}`)
        if (itemID) {
          let popup = document.querySelector(`h1[data-eid="${itemID}"]`)
          if (popup) {
            if (this.mapDef['hide-labels'] !== 'true') {
              popup = popup.parentElement.parentElement.parentElement
              popup.childNodes[0].classList.add('popup-invert')
              popup.childNodes[1].childNodes[0].classList.add('popup-invert')
            }
          } else {
            if (this.popups[itemID]) {
              this.popups[itemID].openOn(this.map)
            }
          }
        }
        if (prior) {
          let popup = document.querySelector(`h1[data-eid="${prior}"]`)
          if (popup) {
            popup = popup.parentElement.parentElement.parentElement
            popup.childNodes[0].classList.remove('popup-invert')
            popup.childNodes[1].childNodes[0].classList.remove('popup-invert')
          }
          if (this.popups[prior] && this.mapDef['hide-labels'] === 'true') {
            this.map.closePopup(this.popups[prior])
          }
        }
        
      },
      immediate: true
    },
    selectedItemID: {
      handler: function (itemID, prior) {
        const layer = Object.values(this.layers).find(layer => layer.options.id === (itemID || prior))
      },
      immediate: true
    },
    layers: {
      handler: function (value, prior) {
        if (this.map) {
          // console.log('layers', this.layers)
          if (Object.keys(this.layers).length > 0) {
            if (this.layersControl) {
              this.map.removeControl(this.layersControl)
            }
            this.layersControl = this.$L.control.layers(
                {}, // baseLayers,
                this.layers, 
                { collapsed: true } //options
              ).addTo(this.map)
          }
          if (this.opacityControl) {
            this.map.removeControl(this.opacityControl)
          }
          const fadeableLayers = {}
          for (let [label, layer] of Object.entries(this.layers)) {
            if (layer.options.type === 'mapwarper') {
              fadeableLayers[label] = layer 
            }
          }
          if (fadeableLayers) {
            this.opacityControl = this.$L.control.opacity(fadeableLayers, { collapsed: true }).addTo(this.map)
          }
        }
      },
      immediate: true
    },
    selected: {
      handler: function (value, prior) {
        const map = document.getElementById('map')
        if (this.isSelected && map && map.style.display === 'none') {
          map.style.display = 'block'
        }
      },
      immediate: true
    },
    height: {
      handler: function () {
        const timeSelectorHeight = this.$refs.timeSelector ? this.$refs.timeSelector.clientHeight : 0
        this.mapHeight = this.height - timeSelectorHeight
        // console.log(`height=${this.height} timeSelectorHeight=${timeSelectorHeight} mapHeight=${this.mapHeight}`)
        const lmap = document.getElementById('lmap')
        if (lmap) {
          lmap.style.height = `${this.mapHeight}px`
          // console.log(`lmap.style.height=${lmap.style.height}`)
          this.map.invalidateSize()
        }
      },
      immediate: false
    },
    activeElements: {
      handler: function () {
        this.updateLayers()
      },
      immediate: false
    },
    mapDef: {
      handler: function (mapDef, prior) {
        const lmap = document.getElementById('lmap')
        if (lmap) {
          if (mapDef) {
            if (this.timeSelector && this.timeSelector !== 'true') {
              const initialRangeDates = this.timeSelector.split(':').map(dateStr => this.parseDate(dateStr).getUTCFullYear())
              this.timeRange = initialRangeDates.length === 2 ? initialRangeDates : [initialRangeDates[0], initialRangeDates[0]]
            } else {
              this.timeRange = []
            }
            this.$nextTick(() => {
              const timeSelectorHeight = this.$refs.timeSelector ? this.$refs.timeSelector.clientHeight : 0
              console.log(`mapDef: timeSelector=${this.timeSelector !== undefined} timeSelectorHeight=${timeSelectorHeight} timeRange=${this.timeRange}`)
              this.mapHeight = this.height - timeSelectorHeight
              const lmap = document.getElementById('lmap')
              lmap.style.height = `${this.mapHeight}px`
              this.map.invalidateSize()
              if (!this.map || this.mapChanged(mapDef, prior)) {
                this.createBaseMap()
              } else {
                this.map.flyTo(mapDef.center || defaults.center, mapDef.zoom || defaults.zoom)
              }
              this.$refs.mapWrapper.style.display = 'block'
            })
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

  .popup-invert {
    background-color: #444 !important;
  }
  .popup-invert h1 {
    color: white !important;
  }

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
