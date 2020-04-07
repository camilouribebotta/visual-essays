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
    img: {}
  }),
  computed: {
    images() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'image') },
    items() {
      console.log('images')
      this.$forceUpdate()
      const items = this.images.map(image => { 
        const mapped = {
          id: image.id,
          src: image.url,
          thumbnail: image.thumbnail || image.url,
          caption: image.title
        }
        console.log(mapped)
        return mapped
      })
      this.currentId = items[0].id
      console.log(this.currentId)
      return items
    },
    viewport() { return {height: this.$store.getters.height, width: this.$store.getters.width} },
    width() { return this.viewport.width/2 },
    height() { return this.viewport.width/2 * .85 }
  },
  mounted() {
    console.log('GalleryImageViewer.mounted')
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
  },
  destroyed() {
    console.log('GalleryImageViewer.destroyed')
  }
}
</script>

<style scoped>
  .lingallery figure {
    background-color: #000;
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