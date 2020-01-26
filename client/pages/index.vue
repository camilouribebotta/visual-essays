<template>
  <v-layout>
    <v-flex>
      <div ref="index" v-html="html"/>
    </v-flex>
  </v-layout>
</template>

<script>
  import axios from 'axios'
  import { parseUrl } from '../utils'

  export default {
    name: 'index',
    data: () => ({
      html: undefined
    }),
    created() {
      this.$store.dispatch('setTitle', process.env.site_title)
      this.$store.dispatch('setBanner', process.env.banner_image)
    },
    mounted() {
      axios.get(`${process.env.app_md_endpoint}/${this.$options.name}.md`)
      .then((resp) => {
        this.html = this.$marked(resp.data)
        this.$nextTick(() => {
          const host = window.location.host
          this.$refs.index.querySelectorAll('a').forEach((link) => {
            const parsedUrl = parseUrl(link.href)
            if (parsedUrl.host === host) {
              link.addEventListener('click', (e) => {
                e.preventDefault()
                const path = parsedUrl.pathname.replace(/^\/visual-essays/, '') // needed for GH Pages
                this.$router.push({path: '/essay', query: { src: `${process.env.app_md_endpoint}${path}` }})
              })
            }
          })
        })
      })
    }
  }
</script>
