# Pose detection
A pose detection tool for computer vision.

[![rickroll.gif](https://i.postimg.cc/QM22zj9W/rickroll.gif)](https://postimg.cc/GBjg8wjc)

# System requirement
- MacOS (m1 or above)
- Windows (not supported yet)
- Gnu/Linux (not supported yet)
- Python 3.12

# Getting started
1. Start the app (backend on port 8000 and frontend on port 8080)
    ``` bash
    ./start.sh
    # or use a video file instead of the camera
    ./start.sh --video_source videos/tony_skate.mp4
    # or start just one half
    ./start.sh --backend-only
    ./start.sh --web-only
    ```
