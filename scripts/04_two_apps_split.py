import queue
import numpy as np
import sounddevice as sd


LEFT_IN = "Voicemeeter Out B1"    # lecture  -> left ear
RIGHT_IN = "Voicemeeter Out B2"   # music    -> right ear
OUT_NAME = "Airdopes 91"          # your earphones

FS = 48000
BLOCK = 1024                      # samples per chunk (about 21 ms)
LEFT_GAIN = 1.0
RIGHT_GAIN = 0.6                  # music a bit quieter than the lecture


def find_device(name_part, kind, api_name="Windows WASAPI"):
    key = "max_input_channels" if kind == "input" else "max_output_channels"
    need = 1 if kind == "input" else 2
    for i, d in enumerate(sd.query_devices()):
        api = sd.query_hostapis(d["hostapi"])["name"]
        if api == api_name and d[key] >= need and name_part.lower() in d["name"].lower():
            return i
    raise RuntimeError(f"No WASAPI {kind} device matching '{name_part}'")



def make_input_callback(q, label):
    def callback(indata, frames, time, status):
        if status:
            print(f"{label} input:", status)
        mono = indata.mean(axis=1)            # stereo -> mono: (L + R) / 2
        try:
            q.put_nowait(mono.copy())
        except queue.Full:
            pass                              # output is behind, drop this chunk
    return callback


q_left = queue.Queue(maxsize=8)
q_right = queue.Queue(maxsize=8)


def out_callback(outdata, frames, time, status):
    if status:
        print("output:", status)
    outdata.fill(0)                           # silence in both ears by default
    for ch, q, gain in ((0, q_left, LEFT_GAIN), (1, q_right, RIGHT_GAIN)):
        try:
            block = q.get_nowait()
        except queue.Empty:
            continue                          # that source has nothing ready
        n = min(len(block), frames)
        outdata[:n, ch] = np.clip(block[:n] * gain, -1.0, 1.0)


left_dev = find_device(LEFT_IN, "input")
right_dev = find_device(RIGHT_IN, "input")
out_dev = find_device(OUT_NAME, "output")
print(f"Left source: {left_dev} | Right source: {right_dev} | Output: {out_dev}")

wasapi = sd.WasapiSettings(auto_convert=True)
common = dict(samplerate=FS, blocksize=BLOCK, dtype="float32", extra_settings=wasapi)

with sd.InputStream(device=left_dev, channels=2, callback=make_input_callback(q_left, "left"), **common), \
     sd.InputStream(device=right_dev, channels=2, callback=make_input_callback(q_right, "right"), **common), \
     sd.OutputStream(device=out_dev, channels=2, callback=out_callback, **common):
    input("Lecture -> LEFT ear, music -> RIGHT ear. Press Enter to stop.\n")




  