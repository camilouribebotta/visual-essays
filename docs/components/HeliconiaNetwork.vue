<template>
  <v-container :style="containerStyle">
    <div id="graph"></div>
  </v-container>
</template>

<script>

const data = [
  { label: 'Heliconia tortuosa', source: 'Q3926650', property: 'Can only be pollinated by	Green hermit hummingbird', target: 'Q1076873' },
  { label: 'Heliconia tortuosa', source: 'Q3926650', property: 'Can only be pollinated by	Violet sabrewing hummingbird', target: 'Q1130092' },
  { label: 'Heliconia bihai', source: 'Q2727878', property: 'Is pollinated by	Purple-throated carib (female)', target: 'Q784919' },
  { label: 'Heliconia caribaea', source: 'Q15329469', property: 'Is pollinated by	Purple-throated carib (male)', target: 'Q784919' },
  { label: 'Heliconia chartacea', source: 'Q3926643', property: 'is pollinated by	Hermit hummingbirds', target: 'Q741604' },
  { label: 'Green hermit hummingbird', source: 'Q1076873', property: 'is a species of	Eulampis', target: 'Q263388' },
  { label: 'Violet sabrewing hummingbird', source: 'Q1130092', property: 'is a species of	Campylopterus', target: 'Q535829' },
  { label: 'Purple-throated carib (female)', source: 'Q784919', property: 'is a species of	Eulampis', target: 'Q263388' },
  { label: 'Heliconia tortuosa', source: 'Q3926650', property: 'is a species of	Heliconia', target: 'Q624242' },
  { label: 'Heliconia bihai', source: 'Q2727878', property: 'is a species of Heliconia', target: 'Q624242' },
  { label: 'Heliconia caribaea', source: 'Q15329469', property: 'is a species of Heliconia', target: 'Q624242' },
  { label: 'Heliconia chartacea', source: 'Q3926643', property: 'is a species of Heliconia', target: 'Q624242' },
  { label: 'Campylopterus', source: 'Q535829', property: 'is a genus of	Trochilidae', target: '43624' },
  { label: 'Eulampis', source: 'Q263388', property: 'is a genus of Trochilidae', target: 'Q43624' },
  { label: 'Hermit hummingbirds', source: 'Q741604', property: 'is a subfamily of	Trochilidae', target: 'Q43624' }
]

module.exports = {
  name: 'forceGraph',
  props: { items: Array, width: Number, height: Number },
  data: () => ({
    data
  }),
  computed: {
    containerStyle() { return { width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important' } },
  },
  mounted() {
    this.doQuery(this.items[0].eid)
  },
  methods: {
    drawGraph(data) {
      const items = {}
      data.forEach(item => {
        let obj = items[item.item]
        if (!obj) {
          obj = { 
            id: Object.keys(items).length,
            eid: item.item,
            name: item.itemLabel,
            linksTo: [] 
          }
          items[obj.eid] = obj
        }
        if (item.pic && !obj.img) {
          const fname = decodeURIComponent(item.pic.slice(item.pic.lastIndexOf('/')+1))
          obj.img = new Image()
          obj.img.src = `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(fname)}?width=150`
        }
        if (item.linkTo) {
          obj.linksTo.push(item.linkTo)
        }
      })
      nodes = Object.values(items).filter(item => item.img)

      const links = []
      nodes.filter(node => node.linksTo.length > 0)
        .forEach(node => {
          node.linksTo.forEach(linkTo => {
            if (items[linkTo].img) {
              const link = { source: node.id, target: items[linkTo].id }
              links.push(link)
            }
          })
        })

      const Graph = ForceGraph()
        (document.getElementById('graph'))
        .width(this.width)
        .height(this.height)
        .nodeCanvasObject(({ img, x, y }, ctx) => {
          const size = 12;
          ctx.drawImage(img, x - size / 2, y - size / 2, size, size);
        })
        .cooldownTicks(100)
        .graphData({nodes, links})
        .nodeRelSize(8)
        .nodeLabel('name')
        .linkDirectionalArrowRelPos(1)
        .linkDirectionalArrowLength(4)
        .onNodeDragEnd(node => {
          node.fx = node.x;
          node.fy = node.y;
        })

      // Graph.d3Force('center', null)
      Graph.onEngineStop(() => Graph.zoomToFit(0, 20))
    },
    doQuery(eid) {
      const sparql = `
      SELECT ?item ?itemLabel ?pic ?linkTo
      WHERE {
        ${eid} wdt:P171* ?item
        OPTIONAL { ?item wdt:P171 ?linkTo }
        OPTIONAL { ?item wdt:P18 ?pic }
        SERVICE wikibase:label {bd:serviceParam wikibase:language "en" }
      }`
      return fetch(`https://query.wikidata.org/sparql?query=${encodeURIComponent(sparql)}`, {
        headers: {
          'Accept': 'application/sparql-results+json, application/json',
        }
      }).then(resp => resp.json())
      .then(resp => {
        const items = []
        resp.results.bindings.forEach(res => {
          const item = {}
          for (let [prop, propData] of Object.entries(res)) {
            item[prop] = propData.value
          }
          items.push(item)
        })
        this.drawGraph(items)
      })
    }
   }
}
</script>
