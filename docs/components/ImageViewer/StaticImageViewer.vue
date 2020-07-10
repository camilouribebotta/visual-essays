<template>
  <div>
    <!-- https://github.com/ChristophAnastasiades/Lingallery -->
    <lingallery
      :iid.sync="currentId"
      :width="width"
      :height="height - (images.length === 1 ? 0 : 66)"
      :default-fit="defaultFit"
      :items="images"
      :show-thumbnails="images.length > 1"
      disable-image-click
      background-color="red"
    ></lingallery>
  </div>
</template>

<script>

module.exports = {
  name: 'StaticImageViewer',
  props: {
    items: Array,
    width: Number,
    height: Number,
    defaultFit: {type: String, default: 'cover'}
  },
  data: () => ({
    currentId: undefined
  }),
  computed: {
    images() {
      const images = this.items.map(item => { 
        const mapped = {
          id: item.id,
          src: item.url,
          thumbnail: item.thumbnail || item.url,
          hires: item.hires || item.url,
          caption: item.title ? this.$marked(item.title) : '',
          fit: item.fit || this.defaultFit // 'cover', 'contain;, 'fill', 'scale-down', or null
        }
        return mapped
      })
      this.currentId = images[0].id
      return images
    },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
    isHorizontal() { return this.$store.getters.layout[0] === 'h' },
    footerHeight() { const footerElem = document.getElementById('footer'); return footerElem ? footerElem.clientHeight : 0 },
  },
  mounted() {
    document.querySelectorAll('figure')
      .forEach(fig => {
        fig.addEventListener('click', (e) => {
          if (e.target.tagName === 'IMG') {
            const selected = this.items.find(item => item.url === e.target.src).id
            this.$store.dispatch('setSelectedImageID', selected)
            this.$modal.show('image-viewer-modal')
          }
        })
      })
  }
}
</script>

<style>
  .lingallery figure {
    background-color: #f5f5f5 !important;
  }

  .lingallery_caption {
    font-size: 1.2em !important;
  }

</style>