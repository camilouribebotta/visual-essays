function isMobile() {
    try {
      const isMobile = (/iphone|ipod|android|blackberry|fennec/i).test(navigator.userAgent.toLowerCase()) || (window.innerWidth < 640 && window.innerHeight < 750)
      return isMobile
    } catch (err) {
      return false
    }
  }
  
  export default ({ app }, inject) => {
    const userAgent = window.navigator.userAgent.toLowerCase()
    const isIos = /iphone|ipad|ipod/.test( userAgent )
    const isInStandaloneMode = ('standalone' in window.navigator) && (window.navigator.standalone)
  
    app.store.dispatch('setIsIos', isIos )
    app.store.dispatch('setIsInStandaloneMode', isInStandaloneMode )
    app.store.dispatch('setIsMobile', isInStandaloneMode || isMobile())
  
    const viewport = {
      height: Math.max(document.documentElement.clientHeight, window.innerHeight || 0),
      width: Math.max(document.documentElement.clientWidth, window.innerWidth || 0),
    }
    app.store.dispatch('setViewport', viewport )
    // console.log(`detect-environ: isIos=${isIos} isInStandaloneMode=${isInStandaloneMode} idMobile=${isInStandaloneMode || isMobile()} userAgent=${userAgent} viewport.width=${viewport.width} viewport.height=${viewport.height}`)
  
    let rtime
    let timeout = false
    const delta = 200
  
    function resizeend() {
      if (new Date() - rtime < delta) {
        setTimeout(resizeend, delta)
      } else {
        timeout = false
        const viewport = {
          height: Math.max(document.documentElement.clientHeight, window.innerHeight || 0),
          width: Math.max(document.documentElement.clientWidth, window.innerWidth || 0),
        }
        // console.log(`detect-environ: viewport.width=${viewport.width} viewport.height=${viewport.height}`)
        app.store.dispatch('setViewport', viewport )
      }
    }
  
    app.store.dispatch('setIsOnline', window.navigator.onLine)
    window.addEventListener('online', () => {
      app.store.dispatch('setIsOnline', true )
    })
  
    window.addEventListener('offline', () => {
      app.store.dispatch('setIsOnline', false )
    })
  
    window.addEventListener('resize', () => {
      rtime = new Date()
      if (timeout === false) {
        timeout = true
        setTimeout(resizeend, delta)
      }
    })
  
  }
  