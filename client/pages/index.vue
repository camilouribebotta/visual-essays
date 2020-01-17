<template>
  <v-layout>
    <v-flex>
      <div ref="index" id="index" v-html="index"/>
    </v-flex>
  </v-layout>
</template>

<script>
  import axios from 'axios'

  const api = axios.create({
    baseURL: process.env.ve_service_endpoint
  })

  export default {
    name: 'home',
    data: () => ({
      index: undefined
    }),
    mounted() {
      this.getEssay(this.$route.query.src || process.env.root_essay)
    },
    methods: {
      getEssay(src) {
        api.get(`/essay?src=${encodeURIComponent(src)}&nocss`)
          .then((resp) => { this.index = resp.data })
      }
    },    
    watch: {
      index() {
        // rewrite links with same base url for rendering in app
        const pathElems = (this.$route.query.src || process.env.root_essay).split('/')
        const contentBase = pathElems.slice(0, pathElems.length - 1).join('/')
        this.$nextTick(() => {
          this.$refs.index.querySelectorAll('a').forEach((link) => {
            if (link.href.indexOf(contentBase) === 0) {
              link.addEventListener('click', (e) => {
                e.preventDefault()
                this.$router.push({path: '/essay', query: { src: link.href }})
              })
            }
          })
        })
      }
    }
  }
</script>
