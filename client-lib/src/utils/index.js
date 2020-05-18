
export function parseUrl (href) {
  const match = href.match(/^(https?)\:\/\/(([^:\/?#]*)(?:\:([0-9]+))?)(\/[^?#]*)(\?[^#]*|)(#.*|)$/)
  return match && {
    protocol: match[1],
    host: match[2],
    hostname: match[3],
    origin: `${match[1]}://${match[2]}`,
    port: match[4],
    pathname: match[5],
    search: match[6],
    hash: match[7]
  }
}

export function parseQueryString(queryString) {
    /* eslint-disable no-param-reassign */
    /* eslint-disable no-plusplus */
    queryString = queryString || window.location.search;
    const dictionary = {};
    try {
      if (queryString.indexOf('?') === 0) {
        queryString = queryString.substr(1);
      }
      const parts = queryString.split('&');
      for (let i = 0; i < parts.length; i++) {
        const p = parts[i];
        const keyValuePair = p.split('=');
        if (keyValuePair[0] !== '') {
          const key = keyValuePair[0];
          if (keyValuePair.length === 2) {
            let value = keyValuePair[1];
            // decode URI encoded string
            value = decodeURIComponent(value);
            value = value.replace(/\+/g, ' ');
            dictionary[key] = value;
          } else {
            dictionary[key] = 'true'
          }
        }
      }
    } catch (err) {
      console.log(err);
    }
    return dictionary;
}

export function prepItems(items) {
  items.forEach(item => {
    // ensure each item has both found_in and tagged_in props and 
    // make them a Set for convenient inclusion tests
    item.tagged_in = new Set(item.tagged_in || [])
    item.found_in = new Set(item.found_in || [])
  })
  return items
}

export function elemIdPath(elemId) {
  const elemIds = []
  let elem = document.getElementById(elemId)
  while(elem) {
    elemIds.push(elem.id)
    if (elem.id === 'essay') {
      break
    }
    elem = elem.parentElement
  }
  return elemIds
}

export function itemsInElements(elemIds, items) {
  const selected = []
  const selectedItemIds = new Set()
  for (let i = 0; i < elemIds.length; i++) {
    const eid = elemIds[i]
    items.forEach((item) => {
      if (i === 0 &&
          (item.found_in.has(eid) || item.tagged_in.has(eid)) &&
          !selectedItemIds.has(item.id)) {
        selected.push(item)
        selectedItemIds.add(item.id)
      }
      if (['map', 'map-layer', 'geojson', 'location', 'image', 'video'].includes(item.type) && 
           item.tagged_in.has(eid) && 
           !selectedItemIds.has(item.id)) {
        selected.push(item)
        selectedItemIds.add(item.id)
      }
      /*
      if ((item.type === 'video') && 
           item.tagged_in.has(eid) && 
           !selectedItemIds.has(item.id)) {
        selected.push(item)
        selectedItemIds.add(item.id)
      } 
      */
    })
  }
  return selected
}

export function groupItems(items, components) {
  console.log('groupItems', components)
  const exclude = ['essay']
  const groups = {}
  const maps = items.filter(item => item.type === 'map')
  let selectedMap = maps.length > 0 ? { ...maps[0], ...{layers: {mapwarper:[], geojson:[]}} } : undefined
  if (selectedMap) {
    groups.map = { ...components.map, ...{ items: [selectedMap] } }
  }
  items
    .filter(item => !exclude.includes(item.type))
    .forEach(item => {
      if (item.type === 'entity') {
        if (!groups[item.category]) {
          groups[item.category] = { ...components[item.category], ...{ items: [] } }
        }
        groups[item.category].items.push(item)
      } else if (item.type === 'map-layer') {
        if (selectedMap) {
          if (item['mapwarper-id']) {
            selectedMap.layers.mapwarper.push(item)
          } else if (item.url) {
            selectedMap.layers.geojson.push(item)
          }
        }
      } else {
        const groupName = item.type
        if (!groups[groupName]) { 
          if (item.type === 'image') {
            groups[groupName] = { ...components['image'], ...{ items: [] } }
          } else if (item.type === 'video') {
            groups[groupName] = { ...components['video'], ...{ items: [] } }
          } else {
            groups[groupName] = { ...components[groupName], ...{ items: [] } }
          }
        }
        groups[groupName].items.push(item)
      }
    })
  console.log(groups)
  return groups
}

export function eqSet(as, bs) {
  if (as.size !== bs.size) return false;
  for (var a of as) if (!bs.has(a)) return false;
  return true;
}

export function isMobile() {
  let isMobile = false
  try {
      isMobile = (/iphone|ipod|android|blackberry|fennec/i).test(navigator.userAgent.toLowerCase()) || (window.innerWidth < 640 && window.innerHeight < 750)
  } catch (err) {}
  return isMobile
}

export function throttle(callback, interval) {
  let enableCall = true
  return function(...args) {
    if (!enableCall) return
    enableCall = false
    callback.apply(this, args)
    setTimeout(() => enableCall = true, interval)
  }
}