import queue
import numpy as np
import sounddevice as sd
from .devices import find_device


class SplitterEngine:
    """Plays source A in the left ear and source B in the right ear."""

    def __init__(self, left_name, right_name, out_name,
                 fs=48000, block=1024, left_gain=1.0, right_gain=1.0):
        self.left_dev = find_device(left_name, "input")
        self.right_dev = find_device(right_name, "input")
        self.out_dev = find_device(out_name, "output")
        self.fs, self.block = fs, block
        self.left_gain, self.right_gain = left_gain, right_gain   # can change while running
        self._q_left = queue.Queue(maxsize=8)
        self._q_right = queue.Queue(maxsize=8)
        self._streams = []

    def _input_callback(self, q, label):
        def callback(indata, frames, time, status):
            if status:
                print(f"{label} input:", status)
            try:
                q.put_nowait(indata.mean(axis=1).copy())   # stereo -> mono
            except queue.Full:
                pass
        return callback

    def _output_callback(self, outdata, frames, time, status):
        if status:
            print("output:", status)
        outdata.fill(0)
        for ch, q, gain in ((0, self._q_left, self.left_gain),
                            (1, self._q_right, self.right_gain)):
            try:
                block = q.get_nowait()
            except queue.Empty:
                continue
            n = min(len(block), frames)
            outdata[:n, ch] = np.clip(block[:n] * gain, -1.0, 1.0)

    def start(self):
        common = dict(samplerate=self.fs, blocksize=self.block, dtype="float32",
                      extra_settings=sd.WasapiSettings(auto_convert=True))
        self._streams = [
            sd.InputStream(device=self.left_dev, channels=2,
                           callback=self._input_callback(self._q_left, "left"), **common),
            sd.InputStream(device=self.right_dev, channels=2,
                           callback=self._input_callback(self._q_right, "right"), **common),
            sd.OutputStream(device=self.out_dev, channels=2,
                            callback=self._output_callback, **common),
        ]
        try:
          for s in self._streams:
            s.start()
        except Exception:
            self.stop()
            raise

    def stop(self):
        for s in self._streams:
            s.stop()
            s.close()
        self._streams = []

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()