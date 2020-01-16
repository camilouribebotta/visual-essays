<template>
  <v-layout>
    <v-flex>
      <div ref="main" id="main" v-html="index"/>
    </v-flex>
  </v-layout>
</template>

<script>
import axios from 'axios'
import ResizeSensor from 'resize-sensor'

const baseURL = process.env.deployEnv === 'DEV'
    ? 'http://localhost:5000'
    : 'https://us-central1-visual-essay.cloudfunctions.net'

const api = axios.create({
  baseURL
})

const indexPage = 'Visual_Essays'
export default {
  name: 'visual-essays',
  data: () => ({
    index: undefined
  }),
  mounted() {
    this.getHtml('Visual_Essays')
  },
  methods: {
    getHtml(title) {
      api.get(`/essay?title=${title}&nocss`)
        .then(resp => resp.data)
        .then((html) => { this.index = html })
    }
  },
  watch: {
    index() {
      this.$nextTick(() => {
        this.$refs.main.querySelectorAll('a').forEach((link) => {
          // link.removeAttribute('href')
          link.addEventListener('click', (e) => {
            e.stopPropagation()
            e.preventDefault()
            let title = e.target.attributes.href.value.replace(/\/wiki\//, '')
            this.$router.push(`/essay/${encodeURIComponent(title)}`)
          })
        })
      })
    }
  }
}
</script>
