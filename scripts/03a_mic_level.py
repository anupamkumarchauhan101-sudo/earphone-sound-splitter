import numpy as np
import sounddevice as sd
import time

IN_NAME = "Microphone Array"


def find_input(name_part, api_name="Windows WASAPI"):
    for i, d in enumerate(sd.query_devices()):
        api = sd.query_hostapis(d["hostapi"])["name"]
        if api == api_name and d["max_input_channels"] >= 1 and name_part.lower() in d["name"].lower():
            return i
    raise RuntimeError(f"No WASAPI input matching '{name_part}'")


dev = find_input(IN_NAME)
print("Using input device:", dev, sd.query_devices(dev)["name"])


def cb(indata, frames, t, status):
    if status:
        print("status:", status)
    peak = float(np.abs(indata).max())
    print(f"peak {peak:.4f} " + "#" * int(peak * 200))


with sd.InputStream(device=dev, channels=2, samplerate=48000, blocksize=4800,
                    dtype="float32", callback=cb,
                    extra_settings=sd.WasapiSettings(auto_convert=True)):
    time.sleep(5)