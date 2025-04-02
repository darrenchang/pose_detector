export interface handLandmarksInterface {
  [key: string]: {
    cubeSize: number[]
    cubeColor: string
    position: number[]
    exist: boolean
    display: boolean
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
    display: true,
  },
  thumbCmc: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  thumbMcp: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  thumbIp: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  thumbTip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  indexFingerMcp: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  indexFingerPip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  indexFingerDip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  indexFingerTip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  middleFingerMcp: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  middleFingerPip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  middleFingerDip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  middleFingerTip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  ringFingerMcp: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  ringFingerPip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  ringFingerDip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  ringFingerTip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  pinkyMcp: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  pinkyPip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  pinkyDip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
  },
  pinkyTip: {
    cubeColor: 'orage',
    cubeSize: [0.02, 0.02, 0.02],
    position: [0, 0, 0],
    exist: false,
    display: true,
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

