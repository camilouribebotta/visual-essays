<template>
  <v-container :style="containerStyle">
    <svg id="datavis" :width="width" :height="height"></svg>
  </v-container>
</template>

<script>

  const data = [
    { item: 'Q756', name: 'plant', pic: 'Thanh Long ở Ninh Thuận.jpg', linkTo: 'Q19088' },
    { item: 'Q756', name: 'plant', pic: 'Thanh Long ở Ninh Thuận.jpg', linkTo: 'Q879246' },
    { item: 'Q19088', name: 'eukaryote', pic: 'Eukaryota diversity 2.jpg', linkTo: 'Q2382443' },
    { item: 'Q25314', name: 'angiosperms', pic: 'Sweetbay Magnolia Magnolia virginiana Flower Closeup 2242px.jpg', linkTo: 'Q25814' },
    { item: 'Q25314', name: 'angiosperms', pic: 'Flower poster.jpg', linkTo: 'Q25814' },
    { item: 'Q25814', name: 'seed plants', pic: 'Welwitschia at Ugab River basin.jpg', linkTo: 'Q27133' },
    { item: 'Q25814', name: 'seed plants', pic: 'Welwitschia at Ugab River basin.jpg', linkTo: 'Q642865' },
    { item: 'Q25814', name: 'seed plants', pic: 'Bleeding hearts, Flickr awards.jpg', linkTo: 'Q27133' },
    { item: 'Q25814', name: 'seed plants', pic: 'Bleeding hearts, Flickr awards.jpg', linkTo: 'Q642865' },
    { item: 'Q27133', name: 'vascular plant', pic: 'Leaf 1 web.jpg', linkTo: 'Q756' },
    { item: 'Q27133', name: 'vascular plant', pic: 'Leaf 1 web.jpg', linkTo: 'Q192154' },
    { item: 'Q27133', name: 'vascular plant', pic: 'PinusSylvestris.jpg', linkTo: 'Q756' },
    { item: 'Q27133', name: 'vascular plant', pic: 'PinusSylvestris.jpg', linkTo: 'Q192154' },
    { item: 'Q78961', name: 'monocots', pic: 'Wheat close-up.JPG', linkTo: 'Q25314' },
    { item: 'Q78961', name: 'monocots', pic: 'AlismaPlant1.jpg', linkTo: 'Q25314' },
    { item: 'Q133527', name: 'Streptophyta', pic: 'Ephedra chilensis 1.JPG', linkTo: 'Q11973077' },
    { item: 'Q192154', name: 'Embryophyte', pic: 'Fern.jpg', linkTo: 'Q133527' },
    { item: 'Q203779', name: 'Zingiberales', pic: 'Alpinia zerumbet2CaryCass.jpg', linkTo: 'Q868546' },
    { item: 'Q203779', name: 'Zingiberales', pic: 'Starr 061212-2337 Alpinia purpurata.jpg', linkTo: 'Q868546' },
    { item: 'Q624242', name: 'Heliconia', pic: 'Heliconia rostrata1.jpg', linkTo: 'Q2731188' },
    { item: 'Q624242', name: 'Heliconia', pic: 'Heliconia latispatha (Starwiz).jpg', linkTo: 'Q2731188' },
    { item: 'Q624242', name: 'Heliconia', pic: 'Heliconia Chartacea - Hoomaluhia Botanical Garden.jpg', linkTo: 'Q2731188' },
    { item: 'Q642865', name: 'Euphyllophytina', pic: 'Illustration Crocus vernus0.jpg', linkTo: 'Q27133' },
    { item: 'Q642865', name: 'Euphyllophytina', pic: 'Juglans cinerea.jpg', linkTo: 'Q27133' },
    { item: 'Q868546', name: 'commelinids', pic: 'Beetle palm with nut bunch.jpg', linkTo: 'Q78961' },
    { item: 'Q868546', name: 'commelinids', pic: 'Dactylis glomerata bluete2.jpeg', linkTo: 'Q78961' },
    { item: 'Q879246', name: 'Archaeplastida', pic: 'Bowenia Serrulata in Prague Botanical Garden DSC 0079.jpg', linkTo: 'Q17539327' },
    { item: 'Q879246', name: 'Archaeplastida', pic: 'Ferns02.jpg', linkTo: 'Q17539327' },
    { item: 'Q2382443', name: 'biota', pic: 'Ruwenpflanzen.jpg' },
    { item: 'Q2731188', name: 'Heliconiaceae', pic: 'Heliconia psittacorum (753479962).jpg', linkTo: 'Q203779' },
    { item: 'Q2731188', name: 'Heliconiaceae', pic: 'Heliconia rostrata1.jpg', linkTo: 'Q203779' },
    { item: 'Q11973077', name: 'Viridiplantae', pic: 'Taiwan 2009 East Coast ShihTiPing Giant Stone Steps Algae FRD 6581.jpg', linkTo: 'Q756' },
    { item: 'Q17539327', name: 'Diaphoretickes', linkTo: 'Q19088' }
]

  const graph = {
    nodes: [
      { id: 1, name: 'A' },
      { id: 2, name: 'B' },
      { id: 3, name: 'C' },
      { id: 4, name: 'D' },
      { id: 5, name: 'E' },
      { id: 6, name: 'F' },
      { id: 7, name: 'G' },
      { id: 8, name: 'H' },
      { id: 9, name: 'I' },
      { id: 10, name: 'J' }
    ],
    links: [
      { source: 1, target: 2 },
      { source: 1, target: 5 },
      { source: 1, target: 6 },
      { source: 2, target: 3 },
      { source: 2, target: 7 },
      { source: 3, target: 4 },
      { source: 8, target: 3 },
      { source: 4, target: 5 },
      { source: 4, target: 9 },
      { source: 5, target: 10 }
    ]
  }

module.exports = {
    name: 'network',
    props: { items: Array, width: Number, height: Number },
    data: () => ({
      data
    }),
    computed: {
      containerStyle() { return { width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important' } },
      distinctItems() { const distinct = new Set(); this.data.forEach(item => distinct.add(item.item)); return distinct},
      nodes() { const nodes = {}; this.data.forEach(item => { if (!nodes[item.item]) nodes[item.item] = item}); return Object.values(nodes).map((item, idx) => { return {...item, ...{id: idx} } }) },
      links() { 
        return this.nodes.filter(node => node.linkTo).map(node => { return { source: node.id, target: this.nodes.find(item => item.item === node.linkTo).id } })
      //nodes() { return graph.nodes },
      //links() { return graph.links },
      }
    },
    mounted() {
      console.log(this.distinctItems)
      console.log(this.nodes)
      console.log(this.links)
      this.drawGraph()
    },
    methods: {
      drawGraph() {
        var svg = d3.select('#datavis')

        this.simulation = d3.forceSimulation()
          .force('link', d3.forceLink().id(function(d) { return d.id }))
          .force('charge', d3.forceManyBody().strength(-400))
          .force('center', d3.forceCenter(this.width / 2, this.height / 2))

        var link = svg.append('g')
          .style('stroke', '#aaa')
          .selectAll('line')
          .data(this.links)
          .enter().append('line')

        var node = svg.append('g')
          .attr('class', 'nodes')
          .selectAll('circle')
          .data(this.nodes)
          .enter().append('circle')
          .attr('r', 6)

        var label = svg.append('g')
          .attr('class', 'labels')
          .selectAll('text')
          .data(this.nodes)
          .enter().append('text')
            .attr('class', 'label')
            .text(function(d) { return d.name })

        this.simulation
          .nodes(this.nodes)
          .on('tick', (e) => {
            link
              .attr('x1', function(d) { return d.source.x })
              .attr('y1', function(d) { return d.source.y })
              .attr('x2', function(d) { return d.target.x })
              .attr('y2', function(d) { return d.target.y })

            node
              .attr('r', 20)
              .style('fill', '#d9d9d9')
              .style('stroke', '#969696')
              .style('stroke-width', '1px')
              .attr('cx', function (d) { return d.x+6 })
              .attr('cy', function(d) { return d.y-6 })
        
            label
              .attr('x', function(d) { return d.x })
              .attr('y', function (d) { return d.y })
              .style('font-size', '20px').style('fill', '#4393c3')
          })

        this.simulation.force('link')
          .links(this.links)

      }
    }
  }
</script>
