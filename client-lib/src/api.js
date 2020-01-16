import axios from 'axios'

const baseURL = process.env.NODE_ENV === 'development'
  ? 'http://localhost:5000'
  : 'https://us-central1-visual-essay.cloudfunctions.net'
  // : 'https://23jz6yb4ci.execute-api.us-east-1.amazonaws.com/prod'

export const api = axios.create({
  baseURL
})

export function get_entity(qid, context) {
  let url = `/entity/${qid}`
  if (context) {
    url += `?context=${context}`
  }
    return api.get(url).then(resp => resp.data)
}
