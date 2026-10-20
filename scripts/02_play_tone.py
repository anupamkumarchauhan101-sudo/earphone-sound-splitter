import numpy as np
import sounddevice as sd

DEVICE_NAME = "Airdopes 91"   # part of your earphones' name


def find_output(name_part, api_name="Windows WASAPI"):
    for i, d in enumerate(sd.query_devices()):
        api = sd.query_hostapis(d["hostapi"])["name"]
        if (api == api_name
                and d["max_output_channels"] >= 2
                and name_part.lower() in d["name"].lower()):
            return i
    raise RuntimeError(f"No WASAPI stereo output found matching '{name_part}'")


def make_tone(freq, seconds, side, fs):
    t = np.arange(int(fs * seconds)) / fs
    wave = (0.2 * np.sin(2 * np.pi * freq * t)).astype(np.float32)  # 0.2 = quiet
    out = np.zeros((len(wave), 2), dtype=np.float32)                # column 0 = left, 1 = right
    out[:, 0 if side == "left" else 1] = wave
    return out


device = find_output(DEVICE_NAME)
fs = int(sd.query_devices(device)["default_samplerate"])
print(f"Using device {device} at {fs} Hz")

for side in ("left", "right"):
    print(f"Playing in the {side} ear...")
    sd.play(make_tone(440, 2, side, fs), fs, device=device)
    sd.wait()