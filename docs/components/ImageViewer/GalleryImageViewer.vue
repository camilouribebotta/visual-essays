<template>
  <div>
    <!-- https://github.com/ChristophAnastasiades/Lingallery -->
    <lingallery
      :iid.sync="currentId"
      :width="width"
      :height="height"
      :default-fit="defaultFit"
      :items="items"
      :show-thumbnails="images.length > 1"
      disable-image-click
      background-color="red"
    ></lingallery>
    <hires-image-viewer :img="img"></hires-image-viewer>
  </div>
</template>

<script>

module.exports = {
  name: 'GalleryImageViewer',
  data: () => ({
    currentId: undefined,
    defaultFit: 'cover',
    img: {}
  }),
  computed: {
    images() { return this.$store.getters.itemsInActiveElements.filter(item => item.tag === 'image') },
    items() {
      const items = this.images.map(image => { 
        const mapped = {
          id: image.id,
          src: image.url,
          thumbnail: image.thumbnail || image.url,
          hires: image.hires || image.url,
          caption: image.title ? this.$marked(image.title) : '',
          fit: image.fit || 'cover' // 'cover', 'contain;, 'fill', 'scale-down', or null
        }
        return mapped
      })
      this.currentId = items[0].id
      this.defaultFit = items[0].fit || 'cover'
      return items
    },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
    isHorizontal() { return this.$store.getters.layout[0] === 'h' },
    width() { return Math.min(this.viewport.width, this.maxWidth) / (this.isHorizontal ? 1 : 2)},
    footerHeight() { const footerElem = document.getElementById('footer'); return footerElem ? footerElem.clientHeight : 0 },
    // height() { return this.viewport.height - 175 - (this.items.length === 1 ? 0 :this.footerHeight) }
    height() { return this.$store.getters.height - this.$store.getters.headerHeight - this.$store.getters.footerHeight - (this.items.length === 1 ? 0 : 66)},
  },
  mounted() {
    document.querySelectorAll('figure')
      .forEach(fig => {
        fig.addEventListener('click', (e) => {
          if (e.target.tagName === 'IMG') {
            const selected = this.items.find(item => item.src === e.target.src)
            this.img = {
              caption: selected.caption,
              src: selected.hires,
              width: e.target.naturalWidth,
              height: e.target.naturalHeight 
            }
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

  /*
  .lingallery figure img {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translateY(-50%) translateX(-50%);
  }
  */
</style>