import mediapipe as mp
import time


class Pose():
    # https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker#pose_landmarker_model
    def __init__(self):
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_pose = mp.solutions.pose
        pose_options = {
            "min_detection_confidence": 0.5,
            "min_tracking_confidence": 0.5,
            "enable_segmentation": True,
            "model_complexity": 0,
        }
        self.pose = mp_pose.Pose(**pose_options)

    def inference(self, im):
        results = self.pose.process(im)
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            print(i, landmark)
        return results
