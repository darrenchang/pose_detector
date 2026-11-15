// Shapes returned by POST /api/model/inference_image (see Model.InferenceImage).

export interface RawLandmark {
  index: number
  name: string
  x: number
  y: number
  z: number
  visibility: number
}

export interface ImageInferenceInterface {
  image: {
    filename: string
    width: number
    height: number
  }
  saved_as: string
  // 33 pose landmarks in model order (normalised image coordinates), or []
  pose_landmarks: RawLandmark[]
  // 21 metric world landmarks per detected hand, or []
  hand_landmarks: {
    left: RawLandmark[]
    right: RawLandmark[]
  }
  hand_gestures: {
    left: string
    right: string
  }
}

// One dropped image and the state of its inference request, as shown by a card.
export interface InferenceCard {
  id: string
  name: string
  size: number
  status: 'pending' | 'done' | 'error'
  result?: ImageInferenceInterface
  error?: string
}
