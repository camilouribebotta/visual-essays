<template>
  <v-container id="footer" ref="footer" v-mutate.attr="onMutate" style="z-index:100 !important;">
    <v-row>
      <v-col cols="6" nogutter>
        <img src="https://jstor-labs.github.io/visual-essays/images/labs.jpg" height="30px">
      </v-col>
      <v-col cols="6">
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
  module.exports = {  
    data: () => ({
      height: undefined
    }),
    mounted() {
      console.log('SiteFooter')
      this.height = this.$refs.footer.clientHeight
      this.$emit('footer-height', this.height)
    },
    methods: {
      onMutate(mutations) {
        const mutation = mutations[mutations.length - 1]
        console.log('footer', mutation)
        if (mutation.target && mutation.target.clientHeight !== this.height) {
          this.height = mutation.target.clientHeight
          this.$emit('footer-height', this.height)
        }
      }
    }
  }
</script>

<style>
  
  [v-cloak] { display: none; }
  #footer {
    border: 1px solid #ddd;
    margin: 0;
    max-width: none;
  } 
  .site-footer, .row {
    padding: 0;
    margin: 0;
  }
  .col {
    padding: 0 16px;
  }

</style>