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
            dictionary[key] = ''
          }
        }
      }
    } catch (err) {
      console.log(err);
    }
    return dictionary;
}
  