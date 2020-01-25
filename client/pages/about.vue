<template>
  <v-layout>
    <v-flex>
      <div>src: {{src}}</div>
      <div v-html="html"/>
    </v-flex>
  </v-layout>
</template>

<script>
  export default {
    name: 'about',
    data: () => ({
      html: undefined,
      src: undefined
    }),
    mounted() {
      this.src = `${process.env.app_md_endpoint}/${this.$options.name}.md`
      this.$axios.get(this.src)
      .then(resp => this.html = this.$marked(resp.data))
    }
  }
</script>
