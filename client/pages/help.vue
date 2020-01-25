<template>
  <v-layout>
    <v-flex>
      <div v-html="html"/>
    </v-flex>
  </v-layout>
</template>

<script>
  import axios from 'axios'
  export default {
    name: 'help',
    data: () => ({
      html: undefined
    }),
    mounted() {
      axios.get(`${process.env.app_md_endpoint}/${this.$options.name}.md`)
        .then(resp => this.html = this.$marked(resp.data))
    }
  }
</script>
