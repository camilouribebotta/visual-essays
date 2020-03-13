<template>
  <div>
    <!-- https://github.com/ChristophAnastasiades/Lingallery -->
    <lingallery
      :iid.sync="currentId"
      :width="width"
      :height="height"
      :items="items"
      :showThumbnails="images.length > 1"
      disableImageClick
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
    img: {}
  }),
  computed: {
    images() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'image') },
    items() {
      return this.images.map(img => { return {
        id: img.id,
        src: img.url,
        thumbnail: img.thumbnail || img.url,
        caption: img.title
      }})
    },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
    width() { return this.viewport.width/2 },
    height() { return this.viewport.width/2 * .8 }
  },
  mounted() {
    document.querySelectorAll('figure')
      .forEach(fig => {
        fig.addEventListener('click', (e) => {
          if (e.target.tagName === 'IMG') {
            const selected = this.items.find(item => item.src === e.target.src)
            this.img = {
              caption: selected.caption,
              src: selected.src,
              width: e.target.naturalWidth,
              height: e.target.naturalHeight 
            }
          }
        })
      })
  }
}
</script>

<style scoped>
</style>