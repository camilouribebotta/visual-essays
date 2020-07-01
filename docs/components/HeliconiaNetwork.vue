<template>
  <v-container :style="containerStyle">
    <div id="graph"></div>
  </v-container>
</template>

<script>
  // Uses library https://github.com/vasturiano/force-graph

const data = [
  { label: 'Heliconia tortuosa', img: 'Heliconia-tortuosa.jpg', source: 'Q3926650', property: 'Can only be pollinated by	Green hermit hummingbird', target: 'Q1076873' },
  { label: 'Heliconia tortuosa', img: 'Heliconia-tortuosa.jpg', source: 'Q3926650', property: 'Can only be pollinated by	Violet sabrewing hummingbird', target: 'Q1130092' },
  { label: 'Heliconia bihai', img: 'Heliconia bihai 5379.jpg', source: 'Q2727878', property: 'Is pollinated by	Purple-throated carib (female)', target: 'Q784919' },
  { label: 'Heliconia caribaea', img: 'Heliconia caribaea- Jardin botanique de Deshaies.JPG', source: 'Q15329469', property: 'Is pollinated by	Purple-throated carib (male)', target: 'Q784919' },
  { label: 'Heliconia chartacea', img: 'Heliconia chartacea.JPG', source: 'Q3926643', property: 'is pollinated by	Hermit hummingbirds', target: 'Q741604' },
  { label: 'Green hermit hummingbird', img: 'Green Hermit.jpg', source: 'Q1076873', property: 'is a species of	Eulampis', target: 'Q263388' },
  { label: 'Violet sabrewing hummingbird', img: 'Violet sabrewing (Campylopterus hemileucurus mellitus) male in flight.jpg', source: 'Q1130092', property: 'is a species of	Campylopterus', target: 'Q535829' },
  { label: 'Purple-throated carib (female)', img: 'Purple-throated carib hummingbird.jpg', source: 'Q784919', property: 'is a species of	Eulampis', target: 'Q263388' },
  { label: 'Heliconia tortuosa', img: 'Heliconia-tortuosa.jpg', source: 'Q3926650', property: 'is a species of	Heliconia', target: 'Q624242' },
  { label: 'Heliconia bihai', img: 'Heliconia bihai 5379.jpg', source: 'Q2727878', property: 'is a species of Heliconia', target: 'Q624242' },
  { label: 'Heliconia caribaea', img: 'Heliconia caribaea- Jardin botanique de Deshaies.JPG', source: 'Q15329469', property: 'is a species of Heliconia', target: 'Q624242' },
  { label: 'Heliconia chartacea', img: 'Heliconia chartacea.JPG', source: 'Q3926643', property: 'is a species of Heliconia', target: 'Q624242' },
  { label: 'Campylopterus', img: 'Unbekannter kolibri.jpg', source: 'Q535829', property: 'is a genus of	Trochilidae', target: 'Q43624' },
  { label: 'Eulampis', img: 'Eulampis jugularis a1.jpg', source: 'Q263388', property: 'is a genus of Trochilidae', target: 'Q43624' },
  { label: 'Hermit hummingbirds', img: 'Eutoxeres aquila.jpg', source: 'Q741604', property: 'is a subfamily of	Trochilidae', target: 'Q43624' }
]
// No source defined for Q624242, probably an oversight - need to check with Ashley

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
    this.drawGraph(data)
  },
  methods: {
    drawGraph(data) {
      const items = {}
      data.forEach(item => {
        let obj = items[item.source]
        if (!obj) {
          obj = { 
            id: Object.keys(items).length,
            source: item.source,
            name: item.label,
            targets: [] 
          }
          items[obj.source] = obj
        }
        if (item.img && !obj.img) {
          const fname = decodeURIComponent(item.img.slice(item.img.lastIndexOf('/')+1))
          obj.img = new Image()
          obj.img.src = `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(fname)}?width=150`
        }
        if (item.target) {
          obj.targets.push(item.target)
        }
      })
      nodes = Object.values(items).filter(item => item.img)

      const links = []
      nodes.filter(node => node.targets.length > 0)
        .forEach(node => {
          node.targets.forEach(target => {
            console.log(target, items[target])
            if (items[target] && items[target].img) {
              const link = { source: node.id, target: items[target].id }
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
    }
   }
}
</script>
