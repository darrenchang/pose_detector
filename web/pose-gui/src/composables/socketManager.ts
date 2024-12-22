import { socket } from '@/socket'

export function connect() {
  socket.connect()
}

export function disconnect() {
  socket.disconnect()
}

export function sub(camId: string) {
  socket.emit('subscribe', { cam_id: camId });
}
