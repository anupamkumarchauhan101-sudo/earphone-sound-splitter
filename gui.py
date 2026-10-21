import tkinter as tk
from tkinter import ttk, messagebox

from splitter.devices import list_devices
from splitter.engine import SplitterEngine

# Convenience defaults for your setup; the dropdowns still let you pick anything.
HINTS = {"left": "Out B1", "right": "Out B2", "out": "Airdopes 91"}


def pick(items, hint):
    for item in items:
        if hint.lower() in item.lower():
            return item
    return items[0] if items else ""


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Earphone Sound Splitter")
        self.resizable(False, False)
        self.engine = None

        devices = list_devices()
        inputs = [name for _, name, n_in, _ in devices if n_in >= 1]
        outputs = [name for _, name, _, n_out in devices if n_out >= 2]

        self.left_var = tk.StringVar(value=pick(inputs, HINTS["left"]))
        self.right_var = tk.StringVar(value=pick(inputs, HINTS["right"]))
        self.out_var = tk.StringVar(value=pick(outputs, HINTS["out"]))
        self.lgain = tk.DoubleVar(value=1.0)
        self.rgain = tk.DoubleVar(value=1.0)
        self.llabel = tk.StringVar(value="100%")
        self.rlabel = tk.StringVar(value="100%")
        self.status = tk.StringVar(value="Stopped")

        f = ttk.Frame(self, padding=14)
        f.grid()

        self.combos = []
        for row, (text, var, values) in enumerate([
            ("Left ear source", self.left_var, inputs),
            ("Right ear source", self.right_var, inputs),
            ("Earphones (output)", self.out_var, outputs),
        ]):
            ttk.Label(f, text=text).grid(row=row, column=0, sticky="w", pady=4)
            cb = ttk.Combobox(f, textvariable=var, values=values, width=48, state="readonly")
            cb.grid(row=row, column=1, columnspan=2, padx=8, pady=4)
            self.combos.append(cb)

        for row, (text, var, label) in enumerate([
            ("Left volume", self.lgain, self.llabel),
            ("Right volume", self.rgain, self.rlabel),
        ], start=3):
            ttk.Label(f, text=text).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Scale(f, from_=0.0, to=1.5, variable=var, length=300,
                      command=self.on_gain).grid(row=row, column=1, padx=8, pady=4)
            ttk.Label(f, textvariable=label, width=6).grid(row=row, column=2)

        buttons = ttk.Frame(f)
        buttons.grid(row=5, column=0, columnspan=3, pady=(10, 4))
        self.btn = ttk.Button(buttons, text="Start", width=14, command=self.toggle)
        self.btn.pack(side="left", padx=4)
        ttk.Button(buttons, text="Swap sides", command=self.swap).pack(side="left", padx=4)

        ttk.Label(f, textvariable=self.status).grid(row=6, column=0, columnspan=3)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_gain(self, _=None):
        l, r = self.lgain.get(), self.rgain.get()
        self.llabel.set(f"{int(l * 100)}%")
        self.rlabel.set(f"{int(r * 100)}%")
        if self.engine:                       # applies instantly while playing
            self.engine.left_gain = l
            self.engine.right_gain = r

    def toggle(self):
        self.stop() if self.engine else self.start()

    def start(self):
        try:
            self.engine = SplitterEngine(
                self.left_var.get(), self.right_var.get(), self.out_var.get(),
                left_gain=self.lgain.get(), right_gain=self.rgain.get())
            self.engine.start()
        except Exception as e:
            self.engine = None
            messagebox.showerror("Could not start", str(e))
            return
        self.btn.config(text="Stop")
        self.status.set("Running")
        for cb in self.combos:
            cb.config(state="disabled")

    def stop(self):
        if self.engine:
            self.engine.stop()
            self.engine = None
        self.btn.config(text="Start")
        self.status.set("Stopped")
        for cb in self.combos:
            cb.config(state="readonly")

    def swap(self):
        was_running = self.engine is not None
        if was_running:
            self.stop()
        l, r = self.left_var.get(), self.right_var.get()
        self.left_var.set(r)
        self.right_var.set(l)
        if was_running:
            self.start()

    def on_close(self):
        self.stop()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()