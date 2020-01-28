<template>
  <div ref="imageViewer" id="imageViewer">
    <ul class="listHorizontal">
      <li v-for="image in images" :key="image.id">
        <h3>{{ image.title }}</h3>
        <div :id="image.id" class="image" :style="`width:${viewport.height*0.3}px; height:${viewport.height*0.40}px;`"></div>
      </li>
    </ul>
  </div>
</template>

<script>

export default {
  name: 'ImageViewer',
  data: () => ({}),
  computed: {
    images() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'image') },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} }
  },
  mounted() {
    this.images.forEach((image) => {
      OpenSeadragon({
        id: image.id,
        tileSources: {
          type: 'image',
          url: image.url
        },
        buildPyramid: true,
        showNavigationControl: false
      })
    })
  }
}

</script>

<style>
  h3 {
    font-size: 14pt;
    color: black;
    margin-bottom: 6px;
  }
  .listHorizontal {
    margin-top: 12px;
    display: flex;
    justify-content: space-around;
    color: #b6d8cf;
    font-size:30px;
    text-transform: uppercase;
    list-style: none;
  }

  div.image {
    border: 1px solid #ccc;
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
    text-align: center;
  }

</style>