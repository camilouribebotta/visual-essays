<template>
  <v-layout>
    <v-flex>
      <div>url: {{ url }}</div>
      <div>md: {{ md }}</div>
      <div ref="index" v-html="html"/>
    </v-flex>
  </v-layout>
</template>

<script>
  import axios from 'axios'
  import marked from 'marked'
  import { parseUrl } from '../utils'

  export default {
    name: 'index',
    data: () => ({
      url: undefined,
      md: undefined,
      html: undefined
    }),
    mounted() {
      this.url = `${process.env.app_md_endpoint}/${this.$options.name}.md`
      this.$axios.get(this.url)
      .then((resp) => {
        this.md = resp.data
        this.html = this.$marked(this.md)
        this.$nextTick(() => {
          const host = window.location.host
          this.$refs.index.querySelectorAll('a').forEach((link) => {
            const parsedUrl = parseUrl(link.href)
            if (parsedUrl.host === host) {
              link.addEventListener('click', (e) => {
                e.preventDefault()
                this.$router.push({path: '/essay', query: { src: `${process.env.app_md_endpoint}${parsedUrl.pathname}` }})
              })
            }
          })
        })
      })
    }
  }
</script>
