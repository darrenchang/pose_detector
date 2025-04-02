import { poseLandmarks } from '@/interface/poseLandmarksInterface';
import { leftHandLandmarks, rightHandLandmarks } from '@/interface/handLandmarksInterface';
import { socket } from '@/socket';

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
  Object.keys(poseLandmarks).forEach((key) => {
    poseLandmarks[key].position = [0, 0, 0];
  });

  Object.keys(leftHandLandmarks).forEach((key) => {
    leftHandLandmarks[key].position = [0, 0, 0];
  });

  Object.keys(rightHandLandmarks).forEach((key) => {
    rightHandLandmarks[key].position = [0, 0, 0];
  });

  Object.keys(poseLandmarks).forEach((key, index) => {
    if (message.pose_landmarks.length <= 0) {
      return
    }
    poseLandmarks[key].position = [
      message.pose_landmarks[index]['x'],
      message.pose_landmarks[index]['y'],
      message.pose_landmarks[index]['z'],
    ]
  })
  // Hand landmarks
  Object.keys(leftHandLandmarks).forEach((key, index) => {
    if (message.hand_landmarks.left.length <= 0) {
      return
    }
    leftHandLandmarks[key].position = [
      message.hand_landmarks.left[index]['x'],
      message.hand_landmarks.left[index]['y'],
      message.hand_landmarks.left[index]['z'],
    ]
  })
  Object.keys(rightHandLandmarks).forEach((key, index) => {
    if (message.hand_landmarks.right.length <= 0) {
      return
    }
    rightHandLandmarks[key].position = [
      message.hand_landmarks.right[index]['x'],
      message.hand_landmarks.right[index]['y'],
      message.hand_landmarks.right[index]['z'],
    ]
  })
})
