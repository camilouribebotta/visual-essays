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
      if (['map', 'map-layer', 'geojson', 'location'].includes(item.type) && 
           item.tagged_in.has(eid) && 
           !selectedItemIds.has(item.id)) {
        selected.push(item)
        selectedItemIds.add(item.id)
      }
      if ((item.type === 'video') && 
           item.tagged_in.has(eid) && 
           !selectedItemIds.has(item.id)) {
        selected.push(item)
        selectedItemIds.add(item.id)
      } 
    })
  }
  return selected
}

export function groupItems(items) {
  const exclude = ['essay']
  const groups = {}
  let lastMap = undefined
  items
    .filter(item => !exclude.includes(item.type))
    .forEach(item => {
      if (item.type === 'entity') {
        if (!groups[item.category]) { groups[item.category] = {component: 'entity', label: `${item.category}s`, items: []} }
        groups[item.category].items.push(item)
      } else if (item.type === 'map') {
        if (!groups[item.type]) { groups[item.type] = {component: `g${item.type}`, label: 'Map', items: []}  }
        groups[item.type].items.push(item)
        lastMap = item
        lastMap.layers = {mapwarper:[], geojson:[]}
      } else if (item.type === 'map-layer') {
        if (lastMap) {
          if (item['mapwarper-id']) {
            lastMap.layers.mapwarper.push(item)
          } else if (item['url']) {
            lastMap.layers.geojson.push(item)
          }
        }
      } else {
        const groupName = item.type
        if (!groups[groupName]) { groups[groupName] = {component: `g${item.type}`, label: `${item.type}s`, items: []}  }
        groups[groupName].items.push(item)
      }
    })
  return groups
}