import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


if __name__ == "__main__":
    cap = cv2.VideoCapture(1)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
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
            results = pose.process(img2)
            mp_drawing.draw_landmarks(
                img,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

            cv2.imshow('pose', img)
            if cv2.waitKey(5) == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()
