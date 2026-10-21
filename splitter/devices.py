import sounddevice as sd

API = "Windows WASAPI"


def list_devices():
    """Return (index, name, in_channels, out_channels) for every WASAPI device."""
    result = []
    for i, d in enumerate(sd.query_devices()):
        if sd.query_hostapis(d["hostapi"])["name"] == API:
            result.append((i, d["name"], d["max_input_channels"], d["max_output_channels"]))
    return result


def find_device(name_part, kind):
    """Find a WASAPI device by part of its name. kind is 'input' or 'output'."""
    for i, name, n_in, n_out in list_devices():
        ok = n_in >= 1 if kind == "input" else n_out >= 2
        if ok and name_part.lower() in name.lower():
            return i
    raise RuntimeError(f"No {kind} device matching '{name_part}'. Run with --list to see devices.")