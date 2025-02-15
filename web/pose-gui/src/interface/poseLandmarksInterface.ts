export interface poseLandmarksInterface {
  [key: string]: {
    cubeSize: number[]
    cubeColor: string
    position: number[]
  }
}

export const examplePoseLandmarks: poseLandmarksInterface = {
  // pose landmarks diagram https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker#pose_landmarker_model
  // NOTE: The order of the items must match the pose landmarker model
  // head
  nose: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  leftEyeInner: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
  },
  leftEye: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
  },
  leftEyeOuter: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
  },
  rightEyeInner: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
  },
  rightEye: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
  },
  rightEyeOuter: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
  },
  leftEar: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  rightEar: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  mouthLeft: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  mouthRight: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  // body
  leftShoulder: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightShoulder: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftElbow: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightElbow: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftWrist: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  rightWrist: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  leftPinky: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  rightPinky: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  leftIndex: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  rightIndex: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  leftThumb: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  rightThumb: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  leftHip: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightHip: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftKnee: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightKnee: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftAnkle: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightAnkle: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftHeel: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightHeel: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  leftFootIndex: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
  rightFootIndex: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
  },
}
