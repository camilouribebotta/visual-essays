<template>
  <v-layout>
    <v-flex>
      <div v-html="html"/>
    </v-flex>
  </v-layout>
</template>

<script>
  export default {
    name: 'help',
    data: () => ({
      html: undefined
    }),
    async mounted() {
      this.html = this.$marked(await this.$axios.$get(`${process.env.app_md_endpoint}/${this.$options.name}.md`))
    }
  }
</script>
