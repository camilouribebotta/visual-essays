<template>
  <div id="osd-viewer" :style="containerStyle">
    <button id="caption-box-show" class="button caption-box-show">Show info box</button>
    <div id="caption-box" class="caption-box">
        <div class="caption-box__header">
            <button id="caption-box-hide" class="button button--toggle caption-box-hide">Hide info box</button>
            <div class="caption-box__controls">
                <button id="previous" class="button button__previous">Previous</button>
                <button id="next" class="button button__next">Next</button>
            </div>
        </div>
        <div id="annotation">
        </div>
    </div>
    <div id="osd-viewer"></div>
  </div>
</template>
<script>

module.exports = {
  name: 'StoriiiesViewer',
  props: { items: Array, width: Number, height: Number },
  computed: {
    containerStyle() { return { position: 'relative', width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important' } },
  },
  mounted() {
    var manifest = `https://jqz7t23pp9.execute-api.us-east-1.amazonaws.com/dev/manifest/${this.items[0].id}/manifest.json`
    fetch('https://storiiies.cogapp.com/manifestJSON?manifest=' + manifest).then(resp => resp.json()).then(data => initialiseViewer(data))
  }
}
</script>
<style>

  #osd-viewer {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 100%;
    background: #000;
    border: 1px solid #000; }

  .osd-highlight {
    cursor: pointer;
    box-shadow: 0px 0px 15px 0px rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.6); }

  .caption-box {
    position: absolute;
    display: flex;
    flex-direction: column;
    bottom: 0;
    left: 0;
    padding: 20px;
    width: 100%;
    max-height: 35vh;
    background: rgba(255, 255, 255, 0.85);
    z-index: 10;
    transform: translate(0%, 0%);
    transition: transform 0.3s; }

  .caption-box--hidden {
    transform: translateY(100%); }

  .caption-box__header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem; }

  .button {
    padding: 0;
    background-size: 30px 24px;
    border: none;
    overflow: hidden;
    text-indent: -1000px;
    border: 1px solid transparent; }

  .caption-box-show {
    position: absolute;
    width: 46px;
    height: 46px;
    bottom: 20px;
    left: 20px;
    z-index: 100;
    background: url("../images/show.svg") no-repeat center center;
    background-color: rgba(255, 255, 255, 0.85);
    transition: opacity 0.4s 0s;
    opacity: 0;
    pointer-events: none; }

  .caption-box-show--show {
    opacity: 1;
    pointer-events: all;
    transition-delay: 0.4s; }

  .caption-box__header .button--toggle {
    background: url("../images/hide.svg") no-repeat center center;
    width: 26px; }

  .caption-box__controls .button {
    width: 34px;
    height: 31px;
    background: url("../images/arrow.svg") no-repeat center center; }

  .button:focus {
    outline: none;
    border-color: rgba(0, 0, 0, 0.4); }

  .button__previous {
    transform: rotate(180deg); }

  #annotation {
    overflow: auto; }

  @media screen and (min-width: 42.5rem) {
    .caption-box {
      top: 20px;
      bottom: auto;
      left: 20px;
      width: 40%;
      max-width: 600px;
      max-height: 80vh; }
    .caption-box--hidden {
      transform: translateX(calc(-100% - 5vw)); }
    .caption-box-show {
      bottom: auto;
      top: 33px;
      left: 30px; } }

  canvas {
    transition: transform 1s; }

  body {
    overflow: hidden; }

  canvas.morph {
    transform: translate(25%, -25%) rotateY(0deg) rotateX(45deg) rotateZ(75deg) scale(1) skew(64deg, 14deg);
  }

  .annotation-audio {
    display: block;
    max-width: 100%;
    margin-top: 10px; }

</style>