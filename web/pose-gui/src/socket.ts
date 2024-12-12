import { io } from 'socket.io-client'


// "undefined" means the URL will be computed from the `window.location` object
const URL = 'http://localhost:8000/api/model/get_landmarks'

export const socket = io(URL, {
  path: 'socket.io',
  transports: ['websocket'],
});

// socket.on('connect', () => {
//   state.connected = true
// })
//
// socket.on('disconnect', () => {
//   state.connected = false
// })
//
// socket.on('foo', (...args) => {
//   state.fooEvents.push(args)
// })
//
// socket.on('bar', (...args) => {
//   state.barEvents.push(args)
// })
