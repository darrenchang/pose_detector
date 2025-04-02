export interface poseLandmarksInterface {
  [key: string]: {
    cubeSize: number[]
    cubeColor: string
    position: number[]
    exist: boolean
  }
}

export const poseLandmarks: poseLandmarksInterface = {
  // pose landmarks diagram https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker#pose_landmarker_model
  // NOTE: The order of the items must match the landmarker model
  // head
  nose: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
    exist: false,
  },
  leftEyeInner: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  leftEye: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  leftEyeOuter: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  rightEyeInner: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  rightEye: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  rightEyeOuter: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  leftEar: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
    exist: false,
  },
  rightEar: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
    exist: false,
  },
  mouthLeft: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
    exist: false,
  },
  mouthRight: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
    exist: false,
  },
  // body
  leftShoulder: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
  rightShoulder: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
  leftElbow: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
  rightElbow: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
  leftWrist: {
    cubeColor: 'orage',
    cubeSize: [0.001, 0.001, 0.001],
    position: [0, 0, 0],
    exist: false,
  },
  rightWrist: {
    cubeColor: 'orage',
    cubeSize: [0.001, 0.001, 0.001],
    position: [0, 0, 0],
    exist: false,
  },
  leftPinky: {
    cubeColor: 'orage',
    cubeSize: [0.001, 0.001, 0.001],
    position: [0, 0, 0],
    exist: false,
  },
  rightPinky: {
    cubeColor: 'orage',
    cubeSize: [0.001, 0.001, 0.001],
    position: [0, 0, 0],
    exist: false,
  },
  leftIndex: {
    cubeColor: 'orage',
    cubeSize: [0.001, 0.001, 0.001],
    position: [0, 0, 0],
    exist: false,
  },
  rightIndex: {
    cubeColor: 'orage',
    cubeSize: [0.001, 0.001, 0.001],
    position: [0, 0, 0],
    exist: false,
  },
  leftThumb: {
    cubeColor: 'orage',
    cubeSize: [0.001, 0.001, 0.001],
    position: [0, 0, 0],
    exist: false,
  },
  rightThumb: {
    cubeColor: 'orage',
    cubeSize: [0.001, 0.001, 0.001],
    position: [0, 0, 0],
    exist: false,
  },
  leftHip: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
  rightHip: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
  leftKnee: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
  rightKnee: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
  leftAnkle: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
  rightAnkle: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
  leftHeel: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    exist: false,
    position: [0, 0, 0],
  },
  rightHeel: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
  leftFootIndex: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
  rightFootIndex: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
  },
}
