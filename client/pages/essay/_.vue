<template>
  <v-layout>
    <v-flex>
      <div id="main" v-html="essay"/>
    </v-flex>
  </v-layout>
</template>

<script>
import axios from 'axios'
import ResizeSensor from 'resize-sensor'

const api = axios.create({
  baseURL: process.env.ve_service_endpoint
})

export default {
  name: 'essay',
  data: () => ({
    essay: undefined
  }),
  mounted() {
    this.getEssay(this.$route.params.pathMatch)
  },
  methods: {
    getEssay(title) {
      api.get(`/essay?title=${title}&nocss`)
        .then(resp => resp.data)
        .then((html) => {
          this.essay = html
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
