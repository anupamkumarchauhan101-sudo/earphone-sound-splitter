import numpy as np
import sounddevice as sd

for i, d in enumerate(sd.query_devices()):
    api = sd.query_hostapis(d["hostapi"])["name"]
    if api != "Windows WASAPI" or d["max_input_channels"] < 1:
        continue
    ch = min(d["max_input_channels"], 2)
    try:
        rec = sd.rec(int(2 * 48000), samplerate=48000, channels=ch, device=i,
                     dtype="float32", extra_settings=sd.WasapiSettings(auto_convert=True))
        sd.wait()
        print(f"{i:>3} | peak {np.abs(rec).max():.4f} | {d['name']}")
    except Exception as e:
        print(f"{i:>3} | ERROR {str(e)[:60]} | {d['name']}")
        