import fs from 'fs'
import YAML from 'yaml'

const SETTINGS = YAML.parse(fs.readFileSync('./settings.yaml', 'utf8'))

const BUNDLE_VERSION = require('../package.json').version

const routerBase = {
  'GH_PAGES': { router: { base: SETTINGS.gh_path } }
}[process.env.DEPLOY_ENV] || { router: { base: '/' } }

export default {
  env: { ...SETTINGS,
    deployEnv: process.env.DEPLOY_ENV || 'PROD',
    bundle_version: BUNDLE_VERSION,
    ve_service_endpoint: (process.env.DEPLOY_ENV || 'PROD') === 'PROD'
      ? 'https://us-central1-visual-essay.cloudfunctions.net'
      : 'http://localhost:5000'

  },
  ...routerBase,
  mode: 'spa',
  head: {
    title: SETTINGS.site_title,
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: 'Visual Essays' }
    ],
    script: [
        { src: process.env.DEPLOY_ENV === 'DEV'
          ? 'http://localhost:8081/js/index.js'
          : `https://visual-essays.online/lib/visual-essay-${BUNDLE_VERSION}.min.js` }
      ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
    ]
  },
  plugins: [
    { src: '@/plugins/detect-environment.js', ssr: false },
  ],
  buildModules: [
    '@nuxtjs/vuetify'
  ],
  modules: [
    '@nuxtjs/axios',
  ],
  generate: {
    dir: process.env.DEPLOY_ENV === 'GH_PAGES' ? 'dist' : '../dist',
    fallback: true,
  }
}
