<template>
  <div>
    <v-dialog v-model="show" hide-overlay max-width="80%" @click:outside="$emit('close-viewer')">
      <v-card class="markdown-viewer">
        <v-card-title>
          Markdown source
        </v-card-title>
        <div :style="`height:${height}px;overflow-y:scroll;`">
          <pre v-highlightjs="markdown"><code class="markdown"></code></pre>
        </div>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            text
            @click="$emit('close-viewer')"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>      
    </v-dialog>
  </div>
</template>

<script>
Vue.directive('highlightjs', {
  deep: true,
  bind: function(el, binding) {
    // on first bind, highlight all targets
    let targets = el.querySelectorAll('code')
    targets.forEach((target) => {
      // if a value is directly assigned to the directive, use this
      // instead of the element content.
      if (binding.value) {
        target.textContent = binding.value
      }
      hljs.highlightBlock(target)
    })
  },
  componentUpdated: function(el, binding) {
    // after an update, re-fill the content and then highlight
    let targets = el.querySelectorAll('code')
    targets.forEach((target) => {
      if (binding.value) {
        target.textContent = binding.value
        hljs.highlightBlock(target)
      }
    })
  }
})
module.exports = {
  name: 'markdown-viewer',
  props: {
    markdown: String,
    show: Boolean
  }, 
  data: () => ({
    isOpen: false,
    height: 600
  })
}
</script>

<style>

  .v-application code {
    color: #000;
    font-weight: normal;
  }

  .xml {
    background-color: rgba(255, 255, 102, 0.3);
    color: #000;
  }

  .hljs{display:block;overflow-x:auto;padding:0.5em;background:#F0F0F0}
  .hljs,.hljs-subst{color:#444}
  .hljs-comment{color:#888888}
  .hljs-keyword,.hljs-attribute,.hljs-selector-tag,.hljs-meta-keyword,.hljs-doctag,.hljs-name{font-weight:bold}
  .hljs-type,.hljs-string,.hljs-number,.hljs-selector-id,.hljs-selector-class,.hljs-quote,.hljs-template-tag,.hljs-deletion{color:#880000}
  .hljs-title,.hljs-section{color:#880000;font-weight:bold}
  .hljs-regexp,.hljs-symbol,.hljs-variable,.hljs-template-variable,.hljs-link,.hljs-selector-attr,.hljs-selector-pseudo{color:#BC6060}
  .hljs-literal{color:#78A960}
  .hljs-built_in,.hljs-bullet,.hljs-code,.hljs-addition{color:#397300}
  .hljs-meta{color:#1f7199}.hljs-meta-string{color:#4d99bf}
  .hljs-emphasis{font-style:italic}
  .hljs-strong{font-weight:bold}

</style>