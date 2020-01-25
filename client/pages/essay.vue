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
            const element = document.getElementById('essay')
            const _this = this
            new ResizeSensor(element, function() {
              const essaySpacer = document.getElementById('essay-spacer')
              _this.$store.dispatch('setSpacerHeight', essaySpacer ? essaySpacer.clientHeight : 0)
            })
          })
        })
    }
  }
}
</script>
