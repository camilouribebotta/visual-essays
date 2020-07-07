<template>
  <div id="image-viewer" >
    <!--
    <div id="image-viewer-controls" @click="click()">
      <v-radio-group
        id="image-viewer-mode-control"
        :value="mode"
        row
        dense
        :hide-details="true"
        color="primary"
      >
        <v-radio label="Default" value="default"></v-radio>
        <v-radio label="Mirador" value="mirador"></v-radio>
      </v-radio-group>
    </div>
    -->
    <component 
      v-bind:is="mode === 'default' ? 'defaultImageViewer' : 'miradorImageViewer'"
      :width="width" :height="height" :seq="seq" :items="items" :default-fit="defaultFit"
    ></component>
  </div>
</template>

<script>

module.exports = {
  name: 'ImageViewer',
  props: {
    seq: {type: Number, default: 1},
    items: Array,
    width: Number,
    height: Number,
    initialMode: { type: String, default: 'default' },
    defaultFit: {type: String, default: 'cover'}
  },
  data: () => ({
    mode: 'default',
  }),
  mounted() {
    console.log(`ImageViewer: seq=${this.seq} initialMode=${this.initialMode}`, this.items)
  },
  methods: {
    click() {
      this.mode = this.mode === 'mirador' ? 'default' : 'mirador'
    }
  },
  watch: {
    items: {
      handler: function () {
        console.log('items', this.items)
        const itemWithModeDefined = this.items.find(item => item.mirador || item.default)
        this.mode = itemWithModeDefined
          ? itemWithModeDefined.mirador ? 'mirador' : 'default'
          : this.initialMode
      },
      immediate: true
    }
  }
}
</script>

<style>

  #image-viewer-controls {
    z-index: 300;
    position: absolute;
    height: 36px;
    top: 0px;
    left: 32px;
    /* background-color: #fbfdff; */
    /*border-radius: 4px;*/
    /*box-shadow: 0 1px 5px rgba(0,0,0,0.65);*/
    padding: 20px 10px !important;
    height: 70px !important;
  }

  #image-viewer-mode-control {
    position: relative;
    top: -10px;
    background: white;
    padding: 8px;
    border-radius: 8px;
    opacity: 1.0;
  }

  .v-application .accent--text {
    color: #1D5BC2 !important;
  }

  .v-input {
    margin: 2px 0 0 4px !important;
  }

  .component {
    position: relative;
  }

</style>