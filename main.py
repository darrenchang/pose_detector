import cv2
import mediapipe as mp

from pose.Pose import Pose
from pose.World import World

if __name__ == "__main__":
    pose = Pose()
    world = World()
    cap = cv2.VideoCapture(0)
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while True:
        ret, img = cap.read()
        if not ret:
            print("Cannot receive frame")
            break
        img = cv2.resize(img, (1920, 1080))
        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results, landmarks = pose.inference(img2)
        # mp_drawing.draw_landmarks(
        #     img,
        #     results.pose_landmarks,
        #     mp.solutions.pose.POSE_CONNECTIONS,
        #     landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
        # )
        world.draw_pose_landmarks(landmarks)
        # cv2.imshow("pose", img)
        # if cv2.waitKey(5) == ord("q"):
        #     break
    cap.release()
    cv2.destroyAllWindows()
