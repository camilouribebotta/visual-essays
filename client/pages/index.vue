<template>
  <v-layout>
    <v-flex>
      <div>src: {{src}}</div>
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
      html: undefined,
      src: undefined
    }),
    mounted() {
      this.src = `${process.env.app_md_endpoint}/${this.$options.name}.md`
      this.$axios.get(this.src)
      .then((resp) => {
        this.html = this.$marked(resp.data)
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
