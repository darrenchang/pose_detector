import os
from threading import Condition, Thread
from time import perf_counter, sleep

import cv2

from pose.Logger import Logger

logger = Logger(__file__).get_logger()


class Camera:
    """Background frame reader around ``cv2.VideoCapture``.

    A daemon thread keeps pulling frames from the source and stores the newest
    one on ``self.frame``. Consumers never call ``cap.read()`` themselves: they
    read ``camera.frame`` whenever they want to run inference, or iterate
    ``camera.frames()`` to be handed every new frame as it arrives.

    Opening the source, retrying failed reads and rewinding looping video files
    all live here, so the inference side has no capture logic at all.
    """

    def __init__(self, source: str | int, max_consecutive_failures: int = 100):
        if isinstance(source, str) and source.isdigit():
            # if the input value isdigit, then it's most likely a video cam
            source = int(source)
        self.source = source
        self.max_consecutive_failures = max_consecutive_failures

        # Latest frame as returned by cv2 (BGR), or None before the first read.
        self.frame = None
        # Increments on every successfully read frame; lets consumers tell a
        # new frame apart from the one they already processed.
        self.frame_id = 0
        # perf_counter() at the moment self.frame was captured.
        self.timestamp = 0.0
        # Measured capture rate of the source.
        self.fps = 0.0

        self._new_frame = Condition()
        self._running = False

        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            logger.error(
                f"Cannot open camera/video source {source!r}. "
                "On macOS, make sure the app you launched this from has camera "
                "permission (System Settings > Privacy & Security > Camera). "
                "Shutting down the pose service."
            )
            # Raising here would only reach whichever thread built us; kill the
            # process so the launcher watchdog can take the whole service down.
            os._exit(1)

        # A live camera blocks in read() at its own rate, but a video file
        # decodes as fast as the CPU allows; pace files to their native rate so
        # they play back in real time instead of looping thousands of times a
        # second.
        self.native_fps = self.cap.get(cv2.CAP_PROP_FPS) or 0.0
        self._frame_interval = (
            1.0 / self.native_fps
            if isinstance(source, str) and self.native_fps > 0
            else 0.0
        )

        self._running = True
        self._thread = Thread(
            target=self._capture_loop, name="camera-capture", daemon=True
        )
        self._thread.start()

    def _capture_loop(self):
        consecutive_failures = 0
        last = perf_counter()
        while self._running:
            s = perf_counter()
            ret, img = self.cap.read()
            if not ret:
                consecutive_failures += 1
                if consecutive_failures >= self.max_consecutive_failures:
                    logger.error(
                        f"Cannot receive frame from source {self.source!r} after "
                        f"{self.max_consecutive_failures} consecutive attempts. "
                        "Shutting down the pose service."
                    )
                    os._exit(1)
                logger.warning("Cannot receive frame")
                # A video file has reached its end: play it again from the top.
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            consecutive_failures = 0

            now = perf_counter()
            with self._new_frame:
                # cap.read() hands back a fresh array each call, so swapping the
                # reference is enough: readers holding the old frame keep a
                # consistent image and never see a half-written one.
                self.frame = img
                self.frame_id += 1
                self.timestamp = now
                self._new_frame.notify_all()
            self.fps = 1 / (now - last) if now > last else 0.0
            last = now

            remaining = self._frame_interval - (perf_counter() - s)
            if remaining > 0:
                sleep(remaining)

    def wait_for_frame(self, after: int = 0, timeout: float | None = None):
        """Block until a frame newer than ``after`` exists.

        Returns ``(frame_id, frame)``; the frame is ``None`` only if ``timeout``
        elapsed first. Pass the id you were last given to be handed exactly
        the next new frame and never the same one twice.
        """
        with self._new_frame:
            if not self._new_frame.wait_for(
                lambda: self.frame_id > after or not self._running, timeout
            ):
                return after, None
            return self.frame_id, self.frame

    def frames(self):
        """Yield each new frame as it is captured, blocking in between.

        Iterating this is the natural way to drive per-frame work at the
        source's own rate: nothing is yielded twice and nothing is skipped
        unless the consumer falls behind, in which case it gets the newest.
        """
        last_id = 0
        while self._running:
            last_id, frame = self.wait_for_frame(after=last_id)
            if frame is None:
                break
            yield frame

    def release(self):
        """Stop the capture thread and free the underlying source."""
        self._running = False
        with self._new_frame:
            self._new_frame.notify_all()
        if self._thread.is_alive():
            self._thread.join(timeout=2)
        self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.release()
