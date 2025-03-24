export interface handLandmarksInterface {
  [key: string]: {
    cubeSize: number[]
    cubeColor: string
    position: number[]
  }
}

export const exampleHandLandmarks: handLandmarksInterface = {
  // hand landmarks diagram https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker
  // NOTE: The order of the items must match the landmarker model
  wrist: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  thumbCmc: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  thumbMcp: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  thumbIp: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  thumbTip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  indexFingerMcp: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  indexFingerPip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  indexFingerDip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  indexFingerTip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  middleFingerMcp: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  middleFingerPip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  // body
  middleFingerDip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  middleFingerTip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  ringFingerMcp: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  ringFingerPip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  ringFingerDip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  ringFingerTip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  pinkyMcp: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  pinkyPip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  pinkyDip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
  pinkyTip: {
    cubeColor: 'orage',
    cubeSize: [0.05, 0.05, 0.05],
    position: [0, 0, 0],
  },
}
