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
    <hires-image-viewer :img="img"></hires-image-viewer>
  </div>
</template>

<script>

module.exports = {
  name: 'GalleryImageViewer',
  props: {
    items: Array,
    width: Number,
    height: Number,
    defaultFit: {type: String, default: 'cover'}
  },
  data: () => ({
    currentId: undefined,
    img: {}
  }),
  computed: {
    // images() { return this.$store.getters.itemsInActiveElements.filter(item => item.tag === 'image') },
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
      // this.defaultFit = images[0].fit || 'cover'
      return images
    },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
    isHorizontal() { return this.$store.getters.layout[0] === 'h' },
    // width() { return Math.min(this.viewport.width, this.maxWidth) / (this.isHorizontal ? 1 : 2)},
    footerHeight() { const footerElem = document.getElementById('footer'); return footerElem ? footerElem.clientHeight : 0 },
    // height() { return this.viewport.height - 175 - (this.items.length === 1 ? 0 :this.footerHeight) }
    // height() { return this.$store.getters.height - this.$store.getters.headerHeight - this.$store.getters.footerHeight - (this.items.length === 1 ? 0 : 66)},
  },
  mounted() {
    document.querySelectorAll('figure')
      .forEach(fig => {
        fig.addEventListener('click', (e) => {
          if (e.target.tagName === 'IMG') {
            const selected = this.items.find(item => item.url === e.target.src)
            this.img = {
              caption: selected.caption || selected.title || selected.description,
              src: selected.hires || selected.url ,
              width: e.target.naturalWidth,
              height: e.target.naturalHeight 
            }
          }
        })
      })
  },
  watch: {
    /*
    height: {
      handler: function () {
        console.log(`height=${this.height} width=${this.width}`)
      },
      immediate: true
    },
    */
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