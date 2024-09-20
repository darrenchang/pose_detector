import time

import matplotlib.pyplot as plt
import numpy as np

# Turn on interactive mode
plt.ion()

x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)

fig, ax = plt.subplots()
(line,) = ax.plot(x, y)

# Update plot in a loop
for i in range(100):
    y = np.sin(x + i * 0.1)  # Change y data
    line.set_ydata(y)  # Update the data in the plot
    fig.canvas.draw()  # Redraw the current figure
    fig.canvas.flush_events()  # Process UI events
    time.sleep(0.1)  # Pause to see the update

plt.ioff()  # Turn off interactive mode
plt.show()  # Keep the window open after the loop
