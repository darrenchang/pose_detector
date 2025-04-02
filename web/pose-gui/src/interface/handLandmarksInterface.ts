export interface handLandmarksInterface {
  [key: string]: {
    cubeSize: number[]
    cubeColor: string
    position: number[]
    exist: boolean
  }
}

const exampleHandLandmarks: handLandmarksInterface = {
  // hand landmarks diagram https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker
  // NOTE: The order of the items must match the landmarker model
  wrist: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  thumbCmc: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  thumbMcp: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  thumbIp: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  thumbTip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  indexFingerMcp: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  indexFingerPip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  indexFingerDip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  indexFingerTip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  middleFingerMcp: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  middleFingerPip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  middleFingerDip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  middleFingerTip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  ringFingerMcp: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  ringFingerPip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  ringFingerDip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  ringFingerTip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  pinkyMcp: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  pinkyPip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  pinkyDip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
  pinkyTip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
  },
}


export const leftHandLandmarks: handLandmarksInterface = Object.keys(exampleHandLandmarks).reduce((acc, cur: string) => {
  const landmark = structuredClone(exampleHandLandmarks)[cur]
  Object.assign(acc, { [cur]: landmark});
  return acc
}, {})

export const rightHandLandmarks: handLandmarksInterface = Object.keys(exampleHandLandmarks).reduce((acc, cur: string) => {
  const landmark = structuredClone(exampleHandLandmarks)[cur]
  Object.assign(acc, { [cur]: landmark});
  return acc
}, {})

