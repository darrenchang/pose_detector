import { socket } from '@/socket'

export function connect() {
  socket.connect()
}

export function disconnect() {
  socket.disconnect()
}

export function sub() {
  const dd = { cam_id: 'host_cam' }
  socket.emit('subscribe', dd);
}
