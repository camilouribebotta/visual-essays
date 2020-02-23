export function parseUrl (href) {
    /* eslint-disable no-useless-escape */
    const match = href.match(/^(https?\:)\/\/(([^:\/?#]*)(?:\:([0-9]+))?)(\/[^?#]*)(\?[^#]*|)(#.*|)$/)
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