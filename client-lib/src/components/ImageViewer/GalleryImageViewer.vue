<template>
  <div>
    <!-- https://github.com/ChristophAnastasiades/Lingallery -->
    <lingallery
      :iid.sync="currentId"
      :width="width"
      :height="height"
      :defaultFit="defaultFit"
      :items="items"
      :showThumbnails="images.length > 1"
      disableImageClick
      background-color="red"
    />
    <hires-image-viewer :img="img" />
  </div>
</template>

<script>
import HiresImageViewer from './HiresImageViewer'

export default {
  name: 'GalleryImageViewer',
  components: {
    HiresImageViewer
  },
  data: () => ({
    currentId: undefined,
    defaultFit: 'cover',
    img: {}
  }),
  computed: {
    images() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'image') },
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
    height() { return this.viewport.height - 175 - (this.items.length === 1 ? 0 :this.footerHeight) }
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