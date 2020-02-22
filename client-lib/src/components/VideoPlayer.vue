<template>
  <v-card ref="player" class="text-xs-center">
    <youtube
      v-if="playerWidth"
      ref="youtube"
      :video-id="videoId"
      :width="playerWidth - 12"
      :player-vars="playerVars"
      @ready="ready"
      @playing="playing"
      @paused="paused"
    />
  </v-card>
</template>

<script>

export default {
  name: 'VideoPlayer',
  props: {
    items: { type: Array, default: () => ([]) }
  },
  data: () => ({
    playerVars: {
      ytpPauseOverlay: 0
    },
    isPlaying: false,
    playerWidth: 564
  }),
  computed: {
    videoId() { return this.items[0].id },
    player() { return this.$refs.youtube ? this.$refs.youtube.player : null }
  },
  beforeDestroy() {
    this.isPlaying = false
    if (this.isPlaying) {
      this.player.stopVideo()
    }
  },
  methods: {
    playVideo() {
      this.player.playVideo()
    },
    playing() {
      this.isPlaying = true
    },
    paused() {
      this.isPlaying = false
    },
    ready() {
      console.log('Video player ready')
    }
  }
}
</script>
