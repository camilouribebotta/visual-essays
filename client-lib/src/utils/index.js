
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
          (item.found_in !== undefined && item.tagged_in !== undefined) &&
          (item.found_in.has(eid) || item.tagged_in.has(eid)) &&
          !selectedItemIds.has(item.id)) {
        selected.push(item)
        selectedItemIds.add(item.id)
      }
      if (['map', 'map-layer', 'geojson', 'location', 'image', 'video'].includes(item.tag) && 
           item.tagged_in.has(eid) && 
           !selectedItemIds.has(item.id)) {
        selected.push(item)
        selectedItemIds.add(item.id)
      }
    })
  }
  return selected
}

export function groupItems(items, componentSelectors) {
  const exclude = ['essay']
  const groups = {}
  if (componentSelectors && componentSelectors.tag && componentSelectors.tag.map) {
    const maps = items.filter(item => item.tag === 'map')
    let selectedMap = maps.length > 0 ? { ...maps[0], ...{ layers: [] } } : undefined
    if (selectedMap) {
      groups.mapViewer = { ...componentSelectors.tag.map[0], ...{ items: [selectedMap] } }
      items.filter(item => item.tag === 'map-layer').forEach(layer => selectedMap.layers.push(layer))
    }
  }
  
  items
    .filter(item => !exclude.includes(item.tag))
    .forEach(item => {
      for (let [field, values] of Object.entries(componentSelectors)) {
        if (item[field] && values[item[field]]) {
          values[item[field]].forEach(component => {
            if (!groups[component.name]) {
              groups[component.name] = { ...component, ...{ items: [] } }
            }
            groups[component.name].items.push(item)
          })
        }
      }
    })
  console.log('groups', groups)
  return groups
}

export function eqSet(as, bs) {
  if (as.size !== bs.size) return false;
  for (var a of as) if (!bs.has(a)) return false;
  return true;
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