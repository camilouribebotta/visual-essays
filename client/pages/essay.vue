<template>
  <v-layout>
    <v-flex>
      <div ref="main" id="main" v-html="essay"/>
    </v-flex>
  </v-layout>
</template>

<script>
import axios from 'axios'
import ResizeSensor from 'resize-sensor'

export default {
  name: 'essay',
  data: () => ({
    essay: undefined
  }),
    created() {
      window.data = undefined
      this.$store.dispatch('setTitle', process.env.site_title)
      this.$store.dispatch('setBanner', process.env.banner_image)
    },
  mounted() {
    const src = this.$route.query.src.replace(/http:\/\/localhost:5000/, 'file://localhost')
    console.log('essay', src, process.env.ve_service_endpoint)
    this.getEssay(src)
  },
  methods: {
    getEssay(src) {
      let url = `${process.env.ve_service_endpoint}/essay?src=${encodeURIComponent(src)}&nocss`
      if (process.env.context) {
        url += `&context=${process.env.context}`
      }
      console.log(url)
      axios.get(url)
        .then((resp) => {
          this.essay = resp.data
          this.$nextTick(() => {
            const essay = document.getElementById('essay')
            this.getEssayMetadata(essay)
            const _this = this
            new ResizeSensor(essay, function() {
              const essaySpacer = document.getElementById('essay-spacer')
              _this.$store.dispatch('setSpacerHeight', essaySpacer ? essaySpacer.clientHeight : 0)
            })
          })
        })
    },
    addMetadata() {
      if (window.data) {
        window.data.forEach((item) => {
          if (item.type === 'essay') {
            if (item.title) {
              this.$store.dispatch('setTitle', item.title)
            }
            if (item.banner) {
              this.$store.dispatch('setBanner', item.banner)
            }          }
        })
      } else {
        setTimeout(() => { this.addMetadata() }, 200)
      }
    },
    getEssayMetadata(essay) {
      if (!window.data) {
        essay.querySelectorAll('script[type="application/ld+json"]').forEach((scr) => {
          eval(scr)
        })
      }
      this.addMetadata()
    }
  }
}
</script>
