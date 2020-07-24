<template>
  <div id="mapWrapper" ref="mapWrapper" class="row wrapper">
    <div ref="map" id="lmap" class="lmap" :style="`width:${width}px; height:${mapHeight}px; margin:0;`"></div>
    <div ref="timeSelector" v-if="timeRange.length > 0" style="height: 45px; padding: 0 24px;">
      <!-- https://nightcatsama.github.io/vue-slider-component -->
      <vue-slider
        v-if="max"
        v-model="timeRange"
        :min="min" 
        :max="max"
        :marks="mark"
        :tooltip-formatter="label"
        @change="throttledMethod"
      />
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
    featureDates: new Set(),
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
  created() {
    if (this.timeSelector) {
      if (this.timeSelector !== 'true') {
        const initialRangeDates = this.timeSelector.split(':').map(dateStr => this.parseDate(dateStr).getUTCFullYear())
        this.timeRange = initialRangeDates.length === 2 ? initialRangeDates : [initialRangeDates[0], initialRangeDates[0]]
      }
      this.useTimeSelector = true
      console.log(`timeSelector: start=${this.timeRange[0]} end=${this.timeRange[1]}`)
    }
  },
  mounted() {
    console.log(`MapViewer.mounted: height=${this.height} width=${this.width}`)
    const timeSelectorHeight = this.$refs.timeSelector ? this.$refs.timeSelector.clientHeight : 0
    console.log(`height=${this.height} timeSelectorHeight=${timeSelectorHeight} mapHeight=${this.mapHeight}`)
    this.mapHeight = this.height - timeSelectorHeight
    this.$nextTick(() => { this.createBaseMap() })
  },
  methods: {
    throttledMethod: _.debounce(function (e) {
      console.log('rangeChange', e, this.map)
      console.log('layers', this.layers)
      this.map.removeLayer(this.layers.Labels)
      this.map.eachLayer(layer => {
        console.log(layer.options.id, layer.options.type)
        console.log(layer.options)
        if (layer.options.type === 'geojson' && layer.options.id && layer.options.id.indexOf('map-layer-1') === 0) {
          console.log('removing', layer.options.id)
          this.map.removeLayer(layer)
        }
      })
      this.syncLayers()
    }, 500),
    timeRangeFilter(feature) {
      console.log('filter', feature)
      if (this.timeRange.length === 2) {
        const featureDate = feature.properties.date ? this.parseDate(feature.properties.date).getUTCFullYear() : null
        if (featureDate) {
          this.featureDates.add(featureDate)
          return featureDate >= this.timeRange[0] && featureDate <= this.timeRange[1]
        }
      }
      return true
    },
    setTimeSelector() {
      const min = Math.min(...this.featureDates)
      this.min = Math.floor(min/100)*100
      const max = Math.max(...this.featureDates)
      this.max = Math.ceil(max/100)*100
      console.log(`min=${this.min} max=${this.max} start=${this.timeRange[0]} end=${this.timeRange[1]}`)
    },
    label(val) {
      return `${Math.abs(val)}${val < 0 ? ' BCE' : ''}`
    },
    mark(val) {
      if (val % 100 === 0) {
        return {label: this.label(val)}
      }
      return false
    },
    parseDate(ds) {
      let date
      if (Number.isInteger(ds)) {
        date = new Date(`${ds}-01-01T00:00:00Z`)
      } else {
        const split = ds.split('-')
        if (split.length === 1) {
          const yr = split[0].toUpperCase().replace(/[\. ]/,'')
          let yrAsInt
          if (yr.indexOf('BC') > 0) { // covers both 'BC' and 'BCE' eras
            yrAsInt = -Math.abs(parseInt(yr.slice(0,yr.indexOf('BCE'))))
          } else if (yr.indexOf('CE') > 0 || yr.indexOf('AD') > 0) {
            yrAsInt = parseInt(yr.slice(0,yr.indexOf('CE')))
          } else {
            yrAsInt = parseInt(ds)
          }
          if (yrAsInt > 0) {
            date = new Date(`${yrAsInt}-01-01T00:00:00Z`)
          } else {
            date = new Date(yrAsInt, 0, 0)
            date.setUTCFullYear(yrAsInt)
          }
        } else if (split.length === 2) {
          date = new Date(`${split[0]}-${split[1]}-01T00:00:00Z`)
        } else if (split.length === 3) {
          date = new Date(`${ds}T00:00:00Z`)
        }
      }
      return date
    },
    rangeChange(e) {
      console.log('rangeChange', e)
    },
    createBaseMap() {
      const t = performance.now()
      if (this.map) {
        this.map.off()
        this.map.remove()
        this.map = undefined
      }
      if (!this.map) {
        this.baseLayer = this.$L.tileLayer(...baseLayers[this.mapDef.basemap || defaults.basemap])
        this.map = this.$L.map('lmap', {
          preferCanvas: true,
          center: this.mapDef.center || defaults.center, 
          zoom: this.mapDef.zoom || defaults.zoom, zoomSnap: 0.1,
          layers: [this.baseLayer]})
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
        console.log(`addPopup: id=${id} label=${label} lagLng=${latLng} offset=${offset}`)
        const popup = L.popup({ ...defaults.popupOptions, ...{ offset: L.point(0, offset || 0)}})
        popup.setLatLng(latLng)
        popup.setContent(`<h1 data-eid="${id}">${label}</h1>`)
        popup.options.id = id
        this.popups[id] = popup
      }
    },
    loadGeojson(def, addToMap) {
      this.geojsonIsLoading = true
      this.cachedGeojson(def)
      .then(data => {
        const self = this
        let layerNum = 0
        let numFeatureLabels = 0
        let geojson = L.geoJson(data, {
          filter: this.timeRangeFilter,
          onEachFeature: function(feature, layer) {
            layer.options.id = def.id
            feature.properties.layerid = def.id
            if (!feature.properties.id) {
              feature.properties.id = layerNum === 0 ? def.id : `${def.id}-${layerNum}`
            }
            // console.log(`feature: id=${feature.properties.id} layerid=${feature.properties.layerid}`)
            self.addEventHandlers(layer, layer.feature.properties.id)
            if (!def.title) {
              const label = feature.properties ? feature.properties.label || feature.properties.name || feature.properties.title || feature.properties['ne:NAME'] || undefined : undefined
              if (label) {
                numFeatureLabels += 1
                feature.properties.label = label
                const latLng = layer.feature.geometry.type === 'Polygon' || layer.feature.geometry.type === 'MultiPolygon' || layer.feature.geometry.type === 'LineString'
                  ? layer.getBounds().getCenter()
                  : layer.getLatLng()
                self.addPopup(feature.properties.id, label, latLng, feature.geometry.type === 'Point' ? -45 : 0)
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
                      width: parseFloat(feature.properties['stroke-width']) || 4,
                      color: feature.properties.stroke || '#FB683F'
                    }
                  })
                }
                const decorator = self.$L.polylineDecorator(polyline, {patterns}).addTo(self.map)
              })
            }
            layerNum += 1
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
          pointToLayer: function(feature, latlng) {
            return self.makeMarker(latlng, feature.properties)
          }
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
          this.addPopup(def.id, geojsonLabel, geojson.getBounds().getCenter())
          this.addEventHandlers(geojson, def.id)
        }

        geojson.options.id = def.id
        geojson.options.label = geojsonLabel
        geojson.options.type = 'geojson'

        console.log(this.active)
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
        this.addPopup(location.eid, markerLabel, marker.getLatLng(), -45)
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
    }
  },
  watch: {
    geojsonIsLoading: {
      handler: function (isLoading, prior) {
        console.log(`watch.geojsonIsLoading=${isLoading} prior=${prior}`)
        if (!isLoading) {
          this.setTimeSelector()
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
        console.log(`height=${this.height} timeSelectorHeight=${timeSelectorHeight} mapHeight=${this.mapHeight}`)
        this.mapHeight = this.height - timeSelectorHeight
        const lmap = document.getElementById('lmap')
        if (lmap) {
          lmap.style.height = `${this.mapHeight}px`
          console.log(`lmap.style.height=${lmap.style.height}`)
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
