// Shared skeleton topology: which landmarks are drawn as joints, how they are
// connected into bones, and the proportions used to size heads and hands.
// Used by the live SkeletonScene and the static per-image PoseCardScene.
import { poseLandmarks } from '@/interface/poseLandmarksInterface'
import { leftHandLandmarks } from '@/interface/handLandmarksInterface'

// Landmark names in model index order (the API returns arrays in this order).
export const POSE_JOINT_NAMES = Object.keys(poseLandmarks)
export const HAND_JOINT_NAMES = Object.keys(leftHandLandmarks)

// --- Body (pose) topology -------------------------------------------------
// The face landmarks (indices 0-10) are not drawn individually; the head is a
// single sphere. The coarse pose hand points are not drawn either; fingers come
// from the dedicated hand landmarks.
export const BODY_JOINTS = [
  'leftShoulder', 'rightShoulder', 'leftElbow', 'rightElbow', 'leftWrist', 'rightWrist',
  'leftHip', 'rightHip', 'leftKnee', 'rightKnee', 'leftAnkle', 'rightAnkle',
  'leftHeel', 'rightHeel', 'leftFootIndex', 'rightFootIndex',
]

export const BODY_CONNECTIONS: [string, string][] = [
  // torso
  ['leftShoulder', 'rightShoulder'], ['leftShoulder', 'leftHip'], ['rightShoulder', 'rightHip'], ['leftHip', 'rightHip'],
  // arms
  ['leftShoulder', 'leftElbow'], ['leftElbow', 'leftWrist'],
  ['rightShoulder', 'rightElbow'], ['rightElbow', 'rightWrist'],
  // legs
  ['leftHip', 'leftKnee'], ['leftKnee', 'leftAnkle'], ['leftAnkle', 'leftHeel'], ['leftHeel', 'leftFootIndex'], ['leftAnkle', 'leftFootIndex'],
  ['rightHip', 'rightKnee'], ['rightKnee', 'rightAnkle'], ['rightAnkle', 'rightHeel'], ['rightHeel', 'rightFootIndex'], ['rightAnkle', 'rightFootIndex'],
]

export function bodyJointRadius(name: string) {
  if (name === 'leftHeel' || name === 'rightHeel' || name === 'leftFootIndex' || name === 'rightFootIndex') {
    return 0.035
  }
  return 0.05
}

// --- Hand topology (21 landmarks per hand) --------------------------------
export const HAND_CONNECTIONS: [string, string][] = [
  // thumb
  ['wrist', 'thumbCmc'], ['thumbCmc', 'thumbMcp'], ['thumbMcp', 'thumbIp'], ['thumbIp', 'thumbTip'],
  // index
  ['wrist', 'indexFingerMcp'], ['indexFingerMcp', 'indexFingerPip'], ['indexFingerPip', 'indexFingerDip'], ['indexFingerDip', 'indexFingerTip'],
  // middle
  ['indexFingerMcp', 'middleFingerMcp'], ['middleFingerMcp', 'middleFingerPip'], ['middleFingerPip', 'middleFingerDip'], ['middleFingerDip', 'middleFingerTip'],
  // ring
  ['middleFingerMcp', 'ringFingerMcp'], ['ringFingerMcp', 'ringFingerPip'], ['ringFingerPip', 'ringFingerDip'], ['ringFingerDip', 'ringFingerTip'],
  // pinky + palm edge
  ['ringFingerMcp', 'pinkyMcp'], ['wrist', 'pinkyMcp'], ['pinkyMcp', 'pinkyPip'], ['pinkyPip', 'pinkyDip'], ['pinkyDip', 'pinkyTip'],
]

// --- Proportions ----------------------------------------------------------
// Everything is sized off the torso length (shoulder-centre to hip-centre),
// which — unlike the shoulder width or the forearm — does not foreshorten when
// the subject turns, so it is a stable size proxy. Hands convert their metric
// landmarks with a fixed nominal span (not the live finger span) so a curled
// fist can't blow the hand up.
export const NOMINAL_HAND_SPAN = 0.18 // typical metric wrist -> middle-fingertip span
export const HAND_TO_TORSO = 0.25 // rendered (open) hand length as a fraction of torso length
export const HEAD_TO_TORSO = 0.26 // head radius as a fraction of torso length
