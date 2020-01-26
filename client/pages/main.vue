<template>
  <v-layout>
    <v-flex>
      <div ref="index" v-html="html"/>
    </v-flex>
  </v-layout>
</template>

<script>
  import axios from 'axios'
  import marked from 'marked'
  import { parseUrl } from '../utils'

  const baseURL = 'https://jstor-labs.github.io/visual-essays/examples'
  const api = axios.create({ baseURL })

  export default {
    name: 'index',
    data: () => ({
      html: undefined
    }),
    mounted() {              
      api.get('/README.md')
      .then((resp) => {
        this.html = marked(resp.data)
        this.$nextTick(() => {
          const host = window.location.host
          this.$refs.index.querySelectorAll('a').forEach((link) => {
            const parsedUrl = parseUrl(link.href)
            console.log(parsedUrl.host === host)
            if (parsedUrl.host === host) {
              link.addEventListener('click', (e) => {
                e.preventDefault()
                this.$router.push({path: '/essay', query: { src: `${baseURL}${parsedUrl.pathname}` }})
              })
            }
          })
        })
      })
    }
  }
</script>
