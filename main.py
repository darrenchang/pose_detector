import cv2
import matplotlib.pyplot as plt
import numpy as np
import mediapipe as mp

from pose.Pose import Pose

if __name__ == "__main__":
    pose = Pose()
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    cap = cv2.VideoCapture(0)
    plt.ion()
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)

    fig, ax = plt.subplots()
    (line,) = ax.plot(x, y)

    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    i = 0
    while True:
        y = np.sin(x + i * 0.1)  # Change y data
        line.set_ydata(y)  # Update the data in the plot
        fig.canvas.draw()  # Redraw the current figure
        fig.canvas.flush_events()  # Process UI events
        i += 1

        ret, img = cap.read()
        if not ret:
            print("Cannot receive frame")
            break
        img = cv2.resize(img, (1920, 1080))
        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.inference(img2)
        mp_drawing.draw_landmarks(
            img,
            results.pose_landmarks,
            mp.solutions.pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
        )
        cv2.imshow("pose", img)
        if cv2.waitKey(5) == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
