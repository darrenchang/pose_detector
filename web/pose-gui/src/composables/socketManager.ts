import { poseLandmarks } from '@/interface/poseLandmarksInterface';
import { leftHandLandmarks, rightHandLandmarks, handGestures } from '@/interface/handLandmarksInterface';
import { socket } from '@/socket';

// Consecutive `landmarks` messages in which each detection was missing.
// Reset to 0 on every message that contains it; starts at Infinity so a view
// can tell "never detected yet" apart from "briefly lost".
export const detectionMisses = {
  pose: Number.POSITIVE_INFINITY,
  leftHand: Number.POSITIVE_INFINITY,
  rightHand: Number.POSITIVE_INFINITY,
}

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
  detectionMisses.pose = message.pose_landmarks.length > 0 ? 0 : detectionMisses.pose + 1
  detectionMisses.leftHand = message.hand_landmarks.left.length > 0 ? 0 : detectionMisses.leftHand + 1
  detectionMisses.rightHand = message.hand_landmarks.right.length > 0 ? 0 : detectionMisses.rightHand + 1
  // Pose landmarks
  Object.keys(poseLandmarks).forEach((key, index) => {
    if (message.pose_landmarks.length <= 0) {
      poseLandmarks[key].exist = false;
      return
    }
    poseLandmarks[key].exist = true;
    poseLandmarks[key].position = [
      message.pose_landmarks[index]['x'],
      message.pose_landmarks[index]['y'],
      message.pose_landmarks[index]['z'],
    ]
  })
  // Hand landmarks
  Object.keys(leftHandLandmarks).forEach((key, index) => {
    if (message.hand_landmarks.left.length <= 0) {
      leftHandLandmarks[key].exist = false
      return
    }
    leftHandLandmarks[key].exist = true
    leftHandLandmarks[key].position = [
      message.hand_landmarks.left[index]['x'],
      message.hand_landmarks.left[index]['y'],
      message.hand_landmarks.left[index]['z'],
    ]
  })
  Object.keys(rightHandLandmarks).forEach((key, index) => {
    if (message.hand_landmarks.right.length <= 0) {
      rightHandLandmarks[key].exist = false
      return
    }
    rightHandLandmarks[key].exist = true
    rightHandLandmarks[key].position = [
      message.hand_landmarks.right[index]['x'],
      message.hand_landmarks.right[index]['y'],
      message.hand_landmarks.right[index]['z'],
    ]
  })
  // Hand gestures
  handGestures['right'] = message.hand_gestures.right
  handGestures['left'] = message.hand_gestures.left
})
