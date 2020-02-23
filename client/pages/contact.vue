<template>
  <v-layout>
    <v-flex>
      <div :ref="$options.name" v-html="html"/>
    </v-flex>
  </v-layout>
</template>

<script>
  import Mixin from './mixin'

  export default {
    name: 'about',
    mixins: [ Mixin ],
    mounted() {
      this.getStaticPage(this.$store.getters.pages[this.$options.name])
    }
  }
</script>
