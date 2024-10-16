import json
from time import perf_counter

import cv2
import mediapipe as mp
from redislite import Redis
from World import World


class Pose:
    # https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker#pose_landmarker_model
    def __init__(self, cam: int = 0):
        mp_pose = mp.solutions.pose
        pose_options = {
            "static_image_mode": True,
            "min_detection_confidence": 0.5,
            "min_tracking_confidence": 0.5,
            "enable_segmentation": True,
            "model_complexity": 0,
        }
        self.pose = mp_pose.Pose(**pose_options)

    def inference(self, im):
        results = self.pose.process(im)
        landmarks = []
        if results.pose_landmarks is not None:
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                landmarks.append(
                    {
                        "index": i,
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility,
                    }
                )
        return results, landmarks


if __name__ == "__main__":
    pose = Pose()
    world = World()
    cap = cv2.VideoCapture(0)
    redis_connection = Redis("/tmp/redis.db")
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while True:
        s = perf_counter()
        ret, img = cap.read()
        if not ret:
            print("Cannot receive frame")
            break
        img = cv2.resize(img, (1920, 1080))
        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results, landmarks = pose.inference(img2)
        redis_connection.set("landmarks", json.dumps(landmarks))
        # mp_drawing.draw_landmarks(
        #     img,
        #     results.pose_landmarks,
        #     mp.solutions.pose.POSE_CONNECTIONS,
        #     landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
        # )
        # world.draw_pose_landmarks(landmarks)
        # cv2.imshow("pose", img)
        # redis_connection.get("landmarks")
        print(f"FPS: {1 / (perf_counter() - s)}")
        if cv2.waitKey(5) == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
