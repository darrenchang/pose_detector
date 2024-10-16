import matplotlib.pyplot as plt
from time import perf_counter
# https://threejs.org/docs/index.html#manual/en/introduction/Animation-system


class World():
    def __init__(self):
        plt.ion()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.x_limit = [0, 1]
        self.y_limit = [0, 1]
        self.z_limit = [-2, 2]
        self.set_axis_limits()
        self.dots = []

    def set_axis_limits(self):
        self.ax.set_xlim(self.x_limit)
        self.ax.set_ylim(self.y_limit)
        self.ax.set_zlim(self.z_limit)
        offset = 10
        self.ax.view_init(elev=270 + offset, azim=270)
        self.ax.set_xlabel(f'X axis {tuple(self.x_limit)}')
        self.ax.set_ylabel(f'Y axis {tuple(self.y_limit)}')
        self.ax.set_zlabel(f'Z axis {tuple(self.z_limit)}')

    def draw_pose_landmarks(self, landmarks: list[dict] = []):
        s = perf_counter()
        dots = []
        for index, landmark in enumerate(landmarks):
            x = landmark.get('x', 0)
            y = landmark.get('y', 0)
            z = landmark.get('z', 0)
            if len(self.dots) > 0:
                self.dots[index].remove()
                self.dots[index] = (self.ax.scatter(x, y, z, color='r', s=10))
            else:
                dots.append(self.ax.scatter(x, y, z, color='r', s=10))
        if len(dots) > 0:
            self.dots = dots

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        print(perf_counter() - s)
