<template>
  <v-layout>
    <v-flex>
      <div v-html="html"/>
    </v-flex>
  </v-layout>
</template>

<script>
  export default {
    name: 'contact',
    data: () => ({
      html: undefined
    }),
    mounted() {
      this.$axios.get(`${process.env.app_md_endpoint}/${this.$options.name}.md`)
      .then(resp => this.html = this.$marked(resp.data))
    }
  }
</script>
