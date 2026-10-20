import sounddevice as sd

for i, d in enumerate(sd.query_devices()):
    api = sd.query_hostapis(d["hostapi"])["name"]
    print(f"{i:>3} | {api:<22} | in:{d['max_input_channels']} out:{d['max_output_channels']} | {d['name']}")

    