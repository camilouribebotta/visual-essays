import axios from 'axios'
import { parseUrl } from '../utils'
import ResizeSensor from 'resize-sensor'

export default {
    name: 'main-mixin',
    data: () => ({
      essay: undefined
    }),
    computed: {
      html() { return this.$store.getters.html },
      baseUrl() { return this.$store.getters.baseUrl },
      markup() { return this.$store.getters.markup }
    },
    created() {
      this.$store.dispatch('setTitle', process.env.site_title)
      this.$store.dispatch('setBanner', process.env.banner_image)
    },
    methods: {
      getStaticPage(pageUrl) {
        pageUrl = pageUrl.indexOf('http') === 0 ? pageUrl : `${this.baseUrl}/${pageUrl}`
        const loc = parseUrl(pageUrl)
        let pageType
        if (loc.pathname.slice(loc.pathname.length - 3) === '.md') {
          pageType = 'markdown'
        } else {
          if (loc.pathname.indexOf('/wiki/') === 0 || loc.pathname.indexOf('/w/')) {
            pageType = 'mediawiki'
          }
        }
        console.log(`Page ${this.$options.name}: type=${pageType} url=${pageUrl}`)
        if (pageType === 'markdown') {
          return this.getMarkdown(pageUrl)
          .then((html) => {
            this.$store.dispatch('setHtml', html)
            this.$nextTick(() => { this.updateLinks() })
          })
      } else if (pageType === 'mediawiki') {
          return this.getWikitext(loc.hostname, pageUrl.split('/').slice(4).join('/'))
            .then((html) => {
              this.$store.dispatch('setHtml', html)
              this.$nextTick(() => {
                this.cleanWikitext()
                this.updateLinks()
              })
            })
        }
      },
      getMarkdown(url) {
        return axios.get(url).then(resp => this.$marked(resp.data))
      },
      getWikitext(site, title) {
        return axios.get(`https://${site}/w/api.php?action=parse&format=json&page=${encodeURIComponent(title)}`)
          .then(resp => resp.data.parse ? resp.data.parse.text['*'] : '')
      },
      updateLinks() {
        console.log('updateLinks', this.$options.name)
        if (this.$refs[this.$options.name]) {
          this.$refs[this.$options.name].querySelectorAll('a').forEach((link) => {
            if (link.href) {
              const parsedUrl = parseUrl(link.href)
              console.log(`parsedUrl.origin=${parsedUrl.origin} baseUrl=${this.baseUrl} window.location.origin=${window.location.origin} window.location.hostname=${window.location.hostname} markup=${this.markup}`)
              if ((this.baseUrl.indexOf(parsedUrl.origin) === 0 || window.location.origin === parsedUrl.origin || window.location.hostname === 'localhost') &&
                   link.href.indexOf('#') === -1) {
                // if (parsedUrl.pathname.slice(0, 6) === '/wiki/') {
                if (this.markup === 'wikitext') {
                    if (parsedUrl.pathname.slice(6, 11) === 'File:') {
                    link.href = `${this.baseUrl}/wiki/File:${parsedUrl.pathname.slice(11)}`
                  } else {
                    const essayTitle = parsedUrl.pathname.slice(6)
                    link.removeAttribute('href')
                    link.addEventListener('click', (e) => {
                      this.$router.push(`/essay/${essayTitle}`)
                    })
                  }
                } else {
                  let essayTitle = parsedUrl.pathname.indexOf('/visual-essays/') === 0
                    ? parsedUrl.pathname.slice(15)
                    : parsedUrl.pathname.slice(1)
                  essayTitle = essayTitle.slice(essayTitle.length-3) == '.md' ? essayTitle.slice(0, essayTitle.length-3) : essayTitle
                  link.removeAttribute('href')
                  link.addEventListener('click', (e) => {
                    this.$router.push(`/essay/${essayTitle}`)
                  })                
                }
              }
            }
          })
          this.$refs[this.$options.name].querySelectorAll('img').forEach((img) => {
            const parsedUrl = parseUrl(img.src)
            if (parsedUrl.origin === this.baseUrl || window.location.origin === parsedUrl.origin || window.location.hostname === 'localhost') {
              if (this.markup === 'wikitext') {
                 if (parsedUrl.pathname.slice(0, 10) === '/w/images/') {
                  img.src = `${this.baseUrl}${parsedUrl.pathname}`
                 }
              } else {
                // TODO
              }
            }
          })
        }
      },
      cleanWikitext() {
        if (this.$refs[this.$options.name]) {
          this.$refs[this.$options.name].querySelectorAll('.mw-editsection').forEach(function (a) {
            a.remove()
          })
        }
      },
      getEssay(src) {
        window.data = undefined
        let url = `${process.env.ve_service_endpoint}/essay?src=${encodeURIComponent(src)}&nocss`
        if (process.env.context) {
          url += `&context=${process.env.context}`
        }
        axios.get(url)
          // .then(resp => this.$store.dispatch('setHtml', resp.data))
          .then(resp => this.essay = resp.data)
          .then(essay => this.onLoaded())
      },
      onLoaded() {
        const essayElem = document.getElementById('visual-essay')
        console.log('onLoaded', essayElem)
        if (essayElem) {
          const _this = this
          new ResizeSensor(essayElem, function() {
            const essaySpacer = document.getElementById('essay-spacer')
            _this.$store.dispatch('setSpacerHeight', essaySpacer ? essaySpacer.clientHeight : 0)
          })
          // get essay metadata
          console.log('onLoaded', window.data)
          if (!window.data) {
            const jsonld = essayElem.querySelectorAll('script[type="application/ld+json"]')
            if (jsonld.length > 0) {
              jsonld.forEach((scr) => {
                eval(scr)
              })
            }
          }
          this.addMetadata()
          this.updateLinks()
        } else {
          setTimeout(() => { this.onLoaded() }, 1000)
        }
      },
      addMetadata() {
        if (window.data) {
          window.data.forEach((item) => {
            if (item.type === 'essay') {
              if (item.title) {
                this.$store.dispatch('setTitle', item.title)
              }
              if (item.banner) {
                this.$store.dispatch('setBanner', item.banner)
              }          }
          })
        } else {
          setTimeout(() => { this.addMetadata() }, 1000)
        }
      }
    }
  }
  