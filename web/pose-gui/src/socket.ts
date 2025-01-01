import { reactive } from 'vue'
import { io } from 'socket.io-client'

export const state = reactive({
  connected: false,
})

// "undefined" means the URL will be computed from the `window.location` object
const protocol = window.location.protocol as string
const hostname = window.location.hostname as string
const apiUrl = `${protocol}//${hostname}:8000/api`
const URL = `${apiUrl}/model/get_landmarks`

export const socket = io(URL, {
  path: '/socket.io',
  transports: ['websocket'],
})

socket.on('connect', () => {
  state.connected = true
})

socket.on('disconnect', () => {
  state.connected = false
})
