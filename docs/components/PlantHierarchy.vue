<template>
  <v-container :style="containerStyle">
    <div id="graph"></div>
  </v-container>
</template>

<script>
  // https://github.com/vasturiano/force-graph

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
