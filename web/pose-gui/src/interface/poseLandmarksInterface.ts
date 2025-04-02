export interface poseLandmarksInterface {
  [key: string]: {
    cubeSize: number[]
    cubeColor: string
    position: number[]
    exist: boolean
    display: boolean
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
    display: true,
  },
  leftEyeInner: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  leftEye: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  leftEyeOuter: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  rightEyeInner: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  rightEye: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  rightEyeOuter: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  leftEar: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  rightEar: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  mouthLeft: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  mouthRight: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  // body
  leftShoulder: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  rightShoulder: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  leftElbow: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  rightElbow: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  leftWrist: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: false,
  },
  rightWrist: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: false,
  },
  leftPinky: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: false,
  },
  rightPinky: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: false,
  },
  leftIndex: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: false,
  },
  rightIndex: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: false,
  },
  leftThumb: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: false,
  },
  rightThumb: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: false,
  },
  leftHip: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  rightHip: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  leftKnee: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  rightKnee: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  leftAnkle: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  rightAnkle: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  leftHeel: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    exist: false,
    position: [0, 0, 0],
    display: true,
  },
  rightHeel: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  leftFootIndex: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  rightFootIndex: {
    cubeColor: 'orage',
    cubeSize: [0.1, 0.1, 0.1],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
}
