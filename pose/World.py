import matplotlib.pyplot as plt
from time import perf_counter


class World():
    def __init__(self):
        plt.ion()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.x_limit = [0, 1]
        self.y_limit = [0, 1]
        self.z_limit = [-5, 5]
        self.set_axis_limits()

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
        self.ax.cla()
        self.set_axis_limits()
        for landmark in landmarks:
            x = landmark.get('x', 0)
            y = landmark.get('y', 0)
            z = 0
            self.dots = self.ax.scatter(x, y, z, color='r', s=10)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        print(perf_counter() - s)
