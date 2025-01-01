import { reactive } from 'vue'
import { io } from 'socket.io-client'
import { getBaseApiUrl } from '@/composables/apiUrl'

export const state = reactive({
  connected: false,
})

const URL = `${getBaseApiUrl()}/model/get_landmarks`

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
