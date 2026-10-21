import queue
import numpy as np
import sounddevice as sd

IN_NAME = "Microphone Array"   # laptop mic
OUT_NAME = "Airdopes 91"       # your earphones
FS = 48000
BLOCK = 1024                   # samples per chunk (about 21 ms at 48 kHz)


def find_device(name_part, kind, api_name="Windows WASAPI"):
    key = "max_input_channels" if kind == "input" else "max_output_channels"
    need = 1 if kind == "input" else 2
    for i, d in enumerate(sd.query_devices()):
        api = sd.query_hostapis(d["hostapi"])["name"]
        if api == api_name and d[key] >= need and name_part.lower() in d["name"].lower():
            return i
    raise RuntimeError(f"No WASAPI {kind} device matching '{name_part}'")


in_dev = find_device(IN_NAME, "input")
out_dev = find_device(OUT_NAME, "output")
print(f"Input: {in_dev}  Output: {out_dev}")

q = queue.Queue(maxsize=8)                   # holds chunks between the two streams
wasapi = sd.WasapiSettings(auto_convert=True)  # lets Windows fix sample-rate mismatches


def in_callback(indata, frames, time, status):
    if status:
        print("input:", status)
    mono = indata.mean(axis=1)               # stereo -> mono: (L + R) / 2
    try:
        q.put_nowait(mono.copy())
    except queue.Full:
        pass                                 # output is behind, drop this chunk


def out_callback(outdata, frames, time, status):
    if status:
        print("output:", status)
    outdata.fill(0)                          # start with silence in both ears
    try:
        block = q.get_nowait()
    except queue.Empty:
        return                               # nothing ready, stay silent
    n = min(len(block), frames)
    outdata[:n, 0] = block[:n] * 0.8         # column 0 = LEFT ear only


with sd.InputStream(device=in_dev, channels=2, samplerate=FS, blocksize=BLOCK,
                    dtype="float32", callback=in_callback, extra_settings=wasapi), \
     sd.OutputStream(device=out_dev, channels=2, samplerate=FS, blocksize=BLOCK,
                     dtype="float32", callback=out_callback, extra_settings=wasapi):
    input("Talk into the mic. You should hear yourself in the LEFT ear. Press Enter to stop.\n")