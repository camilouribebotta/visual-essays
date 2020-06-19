<template>
  <div>
    <!-- <div class="text-center">
       <v-btn color="red lighten-2" @click="hiresViewerIsOpen = true">Open dialog</v-btn>
    </div> -->
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
  name: 'DefaultImageViewer',
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
    // () { return this.items.map(item => {return { manifestId: item.manifest } }) },
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
            this.$modal.show('mirador')
            const selected = this.items.find(item => item.url === e.target.src)
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