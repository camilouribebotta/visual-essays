<template>
  <v-layout>
    <v-flex>
      <div>url: {{ url }}</div>
      <div>resp: {{ resp }}</div>
      <div>md: {{ md }}</div>
      <div ref="index" v-html="html"/>
    </v-flex>
  </v-layout>
</template>

<script>
  import axios from 'axios'

  export default {
    name: 'contact',
    data: () => ({
      url: undefined,
      resp: undefined,
      md: undefined,
      html: undefined
    }),
    mounted() {
      this.url = `${process.env.app_md_endpoint}/${this.$options.name}.md`

      axios.get(this.url)
      .then((resp) => {
        this.resp = JSON.stringify(resp)
        this.md = resp.data
        this.html = this.$marked(this.md)
      })
    }
  }
</script>
