<template>
  <v-app>

    <v-navigation-drawer
      v-model="drawer"
      app
      >
      <v-list dense>

        <v-list-item @click="drawer = false" nuxt to="/">
          <v-list-item-action>
            <v-icon>mdi-home</v-icon>
          </v-list-item-action>
          <v-list-item-content>    
            <v-list-item-title>Home</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item @click="drawer = false" nuxt to="/about">
          <v-list-item-action>
            <v-icon>mdi-information</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>About</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item @click="drawer = false" nuxt to="/help">
          <v-list-item-action>
            <v-icon>mdi-help-circle</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Help</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item @click="drawer = false" nuxt to="/contact">
          <v-list-item-action>
            <v-icon>mdi-contact-mail</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Contact</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

      </v-list>
    </v-navigation-drawer>

  <v-card tile class="overflow-hidden">
    <v-app-bar
      app
      prominent
      :height="bannerHeight"
      elevate-on-scroll
      fade-img-on-scroll
      absolute
      dark
      shrink-on-scroll
      :src="banner"
      scroll-target="#scrollableContent"
      scroll-threshold="200"
    >
      <template v-slot:img="{ props }">
        <v-img v-bind="props"/>
      </template>

      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />

      <v-toolbar-title>{{title}}</v-toolbar-title>

      <v-spacer></v-spacer>

    </v-app-bar>

    <v-sheet
      id="scrollableContent"
      class="overflow-y-auto"
    >
      <v-container ref="contentContainer" :style="`margin-top: ${essayTopMargin}px; height: ${height}px;`">
        <nuxt/>
      </v-container>

    </v-sheet>
 
    <v-footer ref="footer" :fixed="fixed" app>
      <v-flex class="text-xs-left">
        <span>&nbsp;v{{ app_version }} ({{ bundle_version }})</span>
      </v-flex>
    </v-footer>

    <v-snackbar
      v-if="logLevel"
      v-model="snackbar"
      :bottom="y === 'bottom'"
      :left="x === 'left'"
      :multi-line="true"
      :right="x === 'right'"
      :timeout="timeout"
      :top="y === 'top'"
      :vertical="false"
    >
      <v-chip :color="loggingConfig[logLevel].color">{{ logMessages[logLevel].length }}</v-chip>
      <span class="log-message">{{ logMessages[logLevel][0] }}</span>
      <v-icon color="red" @click="dismiss">delete</v-icon>
      <v-icon color="white" @click="snackbar = false">close</v-icon>
    </v-snackbar>

  </v-card>
  </v-app>
</template>

<script>

  export default {
    data () {
      return {
        version: process.env.APP_VERSION,
        clipped: true,
        drawer: false,
        fixed: false,
        miniVariant: false,
        height: 600,
        bannerHeight: 600,
        essayTopMargin: 140,
        // title: process.env.site_title,
        app_version: process.env.app_version,
        bundle_version: process.env.bundle_version,
        banner_image: process.env.banner_image,

        snackbar: false,
        y: 'bottom',
        x: null,
        timeout: 0,

        logLevel: null,
        logMenuCount: 0,
        logMenuColor: null,
        loggingConfig: {
          error: { label: 'Error', color: 'red' },
          warning: { label: 'Warning', color: 'yellow' },
          info: { label: 'Info', color: 'teal' },
          debug: { label: 'Debug', color: 'gray' }
        }
      }
    },
    computed: {
      logMessages() { return this.$store.getters.logMessages },
      viewport() { return this.$store.getters.viewport },
      spacerHeight() { return this.$store.getters.spacerHeight },
      title() { return this.$store.getters.title || process.env.site_title },
      banner() { return this.$store.getters.banner || process.env.banner_image }
    },
    mounted() {
      this.bannerHeight = this.viewport.height * .25 
      this.essayTopMargin = this.bannerHeight
      this.height = this.viewport.height - this.bannerHeight - this.spacerHeight - 36
    },
    methods: {
      showLogMessages(level) {
        this.logLevel = level
        this.snackbar = true
      },
      dismiss() {
        if (this.logMessages[this.logLevel].length === 1) {
          this.snackbar = false
          this.logLevel = null
        }
        this.$store.dispatch('popLogMessage', this.logLevel)
      },
    },
    watch: {
      logMessages() {
        this.logMenuCount = 0
        this.logMenuColor = null;
        ['error', 'warning', 'info', 'debug'].forEach((level) => {
          if (this.logMenuCount === 0) {
            if (this.logMessages[level].length > 0) {
              this.logMenuCount = this.logMessages[level].length
              this.logMenuColor = this.loggingConfig[level].color
             }
           }
         })
      },
      viewport: {
        handler: function (viewport) {
          if (viewport) {
            this.bannerHeight = this.viewport.height * .25 
            this.essayTopMargin = this.bannerHeight
            this.height = this.viewport.height - this.bannerHeight - this.spacerHeight - 36
          }
        },
        immediate: true
      }
    }
  }
</script>

<style>
  #keep .v-navigation-drawer__border {
    display: none
  }
  .v-toolbar__title {
    font-size: 24px !important;
    font-weight: bold;
    padding-bottom: 4px !important;
  }

  article,
  aside,
  details,
  figcaption,
  figure,
  footer,
  header,
  hgroup,
  nav,
  section,
  summary {
    display: block;
  }
  html {
    -webkit-text-size-adjust: 100%;
        -ms-text-size-adjust: 100%;
  }
  body {
    /* margin: 20px 60px; */
  }
  ::-moz-selection {
    background-color: hsla(0,0%,0%,.5);
    color: #fff;
    text-shadow: none;
  }
  ::selection {
    background-color: hsla(0,0%,0%,.5);
    color: #fff;
    text-shadow: none;
  }
  a:focus {
    outline: thin dotted;
  }
  a:active,
  a:hover {
    outline: 0;
  }
  strong {
    font-weight: bold;
  }
  mark {
    background: #ff6;
    color: #444;
  }
  code,
  pre {
    font-family: monospace, serif;
    font-size: 1em;
  }
  pre {
    white-space: pre;
  }
  img {
    border: 0;
    max-width: 100%;
    vertical-align: top;
  }
  figure {
    margin: 0;
  }
  button,
  input,
  select,
  textarea {
    font-family: inherit;
    font-size: 100%;
    margin: 0;
  }
  button,
  input {
    line-height: normal;
  }
  button,
  html input[type="button"],
  input[type="reset"],
  input[type="submit"] {
    cursor: pointer;
    -webkit-appearance: button;
  }
  input[type="checkbox"],
  input[type="radio"] {
    box-sizing: border-box;
    padding: 0;
  }
  button::-moz-focus-inner,
  input::-moz-focus-inner {
    border: 0;
    padding: 0;
  }
  textarea {
    overflow: auto;
    vertical-align: top;
  }
  table {
    border-collapse: collapse;
    border-spacing: 0;
  }

  /* Default Typography */

  html {
    color: #444;
    font-family: sans-serif;
    font-size: 100%;
  }
  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    font-weight: bold;
    margin: 0;
  }
  h1 {
    font-size: 3em;
    line-height: 1;
    margin-bottom: .5em;
  }
  h2 {
    font-size: 2.25em;
    line-height: 1.333333333;
    margin-bottom: 0.666666666em;
  }
  h3 {
    font-size: 1.5em;
    line-height: 1;
    margin-bottom: 1em;
  }
  h4 {
    font-size: 1.3125em;
    line-height: 1.142857142;
    margin-bottom: 1.142857142em;
  }
  h5 {
    font-size: 1.125em;
    line-height: 1.333333333;
    margin-bottom: 1.333333333em;
  }
  h6 {
    font-size: 1em;
    line-height: 1.5;
    margin-bottom: 1.5em;
  }
  p,
  blockquote {
    font-size: 1em;
    margin: 0 0 1.5em;
    line-height: 1.5;
    -webkit-hyphens: auto;
        -moz-hyphens: auto;
        -ms-hyphens: auto;
            hyphens: auto;
  }
  p a:link,
  p a:visited {
    border-bottom: 2px solid #6af;
    color: #444;
    padding-bottom: 1px;
    text-decoration: none;
    -webkit-transition: .25s;
        -moz-transition: .25s;
        -ms-transition: .25s;
          -o-transition: .25s;
            transition: .25s;
  }
  p a:hover,
  p a:focus {
    color: #6af;
  }
  p a:active {
    position: relative;
    top: 1px;
    -webkit-transition: none;
        -moz-transition: none;
        -ms-transition: none;
          -o-transition: none;
            transition: none;
  }
  dl,
  ol,
  ul {
    font-size: 1em;
    margin: 0 0 1.5em;
    padding: 0;
  }
  dd,
  dt,
  li {
    line-height: 1.5;
    margin: 0;
  }

  .entity.tagged {
    /* background-color:#eeffcc; */
    border-bottom: 2px solid #c4ff4d;
    /*
    text-decoration: underline;
    text-decoration-color: #c4ff4d;
    */
  }
  .entity.tagged:hover {
    background-color:#eeffcc;
    cursor: pointer;
  }

  .thumbimage {
    border: 1px solid #ccc;
  }

  .thumbcaption {
    margin-top: 6px;
    margin-bottom: 18px;
    font-weight: bold;
    text-align: center;
  }

</style>