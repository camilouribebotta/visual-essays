<template>
  <v-card tile class="overflow-hidden">
    
    <v-navigation-drawer app v-model="drawer" style="z-index:201 !important;">
      <v-list dense v-cloak>
        <v-list-item v-for="(menuItem, i) in nav" :key="i" @click="menuItemClicked(menuItem.file)" v-if="menuItem.enabled">
          <v-list-item-action><v-icon>{{menuItem.icon}}</v-icon></v-list-item-action>
          <v-list-item-content><v-list-item-title>{{menuItem.title}}</v-list-item-title></v-list-item-content>
        </v-list-item>
        <v-divider></v-divider>
        <v-list-item @click="drawer = false; showMarkdown()">
          <v-list-item-action><v-icon>mdi-code-tags</v-icon></v-list-item-action>
          <v-list-item-content><v-list-item-title>View page markdown</v-list-item-title></v-list-item-content>
        </v-list-item>
        <v-divider></v-divider>
        <v-list-item><v-list-item-content style="font-size:0.8em;margin-top:36px;">App version: {{appVersion}}</v-list-item-content></v-list-item>        
        <v-list-item><v-list-item-content style="font-size:0.8em;">Lib version: {{libVersion}}</v-list-item-content></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar
      id="header"
      v-mutate.attr="onMutate"
      app dark dense
      elevate-on-scroll shrink-on-scroll
      elevation="6"
      :src="banner"
      :height="bannerHeight"
      scroll-target="#scrollableContent"
      :scroll-threshold="bannerHeight"
    >

      <v-app-bar-nav-icon large @click.stop="drawer = !drawer" style="padding:0; margin-left:12px; z-index:100; background:rgba(0, 0, 0, .60);"></v-app-bar-nav-icon>

      <v-toolbar-title v-cloak>
        
        <v-container>
          
          <v-row style="margin-left:60px; height:100%;" no-gutters>
            <v-col cols="12" sm="12">
              <h3>{{title}}</h3>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" sm="12" style="padding:6px 0 0 0; margin:0;">
            <v-progress-linear v-model="progress" height="7" color="#70CB2B"></v-progress-linear>
            </v-col>
          </v-row>

        </v-container>
      </v-toolbar-title>
    </v-app-bar>
  </v-card>
</template>

<script>
  module.exports = {
    props: {
      essayConfig: { type: Object, default: function(){ return {}} },
      siteConfig: { type: Object, default: function(){ return {}} },
      progress: { type: Number, default: 0 },
      nav: { type: Array, default: function(){ return []} },
      appVersion: { type: String },
      libVersion: { type: String }
    },    
    data: () => ({
      drawer: false,
      lastHeight: undefined 
    }),
    computed: {
      banner() { return this.essayConfig.banner || this.siteConfig.banner },
      bannerHeight() { return 200 },
      title() { return  this.essayConfig.title || this.siteConfig.title },
      author() { return this.essayConfig.author || '&nbsp;' }
    },
    mounted() {
      document.getElementById('header').addEventListener('wheel', this.throttle(this.scrollContent, 40))
    },
    methods: {
      onMutate(mutations) {
        const mutation = mutations[mutations.length - 1]
        if (mutation.target && mutation.target.clientHeight !== this.lastHeight) {
          this.$emit('header-height', mutation.target.clientHeight)
          this.lastHeight = mutation.target.clientHeight
        }
      },
      menuItemClicked(file) {
        this.drawer = false
        this.$emit('menu-item-clicked', file)
      },
      showMarkdown() {
        this.$emit('show-markdown')
      },
      throttle(callback, interval) {
        let enableCall = true
        return function(...args) {
          if (!enableCall) return
          enableCall = false
          callback.apply(this, args)
          setTimeout(() => enableCall = true, interval)
        }
      },
      scrollContent(e) {
        const wheelDelta = e.wheelDelta
        const scrollableContent = document.getElementById('scrollableContent')
        if (scrollableContent) {
          scrollableContent.scrollTo(0, scrollableContent.scrollTop - wheelDelta)
        }
      }
    }
  }
</script>

<style scoped>

  [v-cloak] { display: none; }

  #header {
    z-index: 200;
  }

  .v-toolbar__content {
    padding: 0;
  }

  .v-toolbar__title {
    width: 100%;
    color: white;
    background-color: rgba(0, 0, 0, .75);
    padding: 0 !important;
    position: absolute;
    top: calc(100% - 48px);
  }

  .v-toolbar__title h3 {
    font-size: 1.5rem;
    margin: 10px 0 6px 6px;
  }

  .v-toolbar__title .container {
    padding: 0;
    max-width: none;
  }

</style>