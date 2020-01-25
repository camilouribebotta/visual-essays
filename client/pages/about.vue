<template>
  <v-layout>
    <v-flex>
      <div>url: {{ url }}</div>
      <div>resp1: {{ resp1 }}</div>
      <div>resp2: {{ resp2 }}</div>
      <div>md: {{ md }}</div>
      <div ref="index" v-html="html"/>
    </v-flex>
  </v-layout>
</template>

<script>
  import axios from 'axios'
  import { parseUrl } from '../utils'

  export default {
    name: 'about',
    data: () => ({
      url: undefined,
      resp1: undefined,
      resp2: undefined,
      md: undefined,
      html: undefined
    }),
    mounted() {
      this.url = `${process.env.app_md_endpoint}/${this.$options.name}.md`

      axios.get(this.url).then(resp => this.resp1 = JSON.stringify(resp))

      this.$axios.get(this.url)
      .then((resp) => {
        this.resp2 = JSON.stringify(resp)
        this.md = resp.data
        this.html = this.$marked(this.md)
      })
    }
  }
</script>
