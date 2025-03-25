import { poseLandmarks } from '@/interface/poseLandmarksInterface'
import { leftHandLandmarks, rightHandLandmarks } from '@/interface/handLandmarksInterface'
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


socket.on('landmarks', message => {
  // Pose landmarks
  Object.keys(poseLandmarks).forEach((key, index) => {
    if (message.pose_landmarks.length <= 0) {
      return
    }
    const position = [
      message.pose_landmarks[index]['x'],
      message.pose_landmarks[index]['y'],
      message.pose_landmarks[index]['z'],
    ]
    poseLandmarks[key].position = position
  })
  // Hand landmarks
  Object.keys(leftHandLandmarks).forEach((key, index) => {
    if (message.hand_landmarks.left.length <= 0) {
      return
    }
    const position = [
      message.hand_landmarks.left[index]['x'],
      message.hand_landmarks.left[index]['y'],
      message.hand_landmarks.left[index]['z'],
    ]
    leftHandLandmarks[key].position = position
  })
  Object.keys(rightHandLandmarks).forEach((key, index) => {
    if (message.hand_landmarks.right.length <= 0) {
      return
    }
    const position = [
      message.hand_landmarks.right[index]['x'],
      message.hand_landmarks.right[index]['y'],
      message.hand_landmarks.right[index]['z'],
    ]
    rightHandLandmarks[key].position = position
  })
})
