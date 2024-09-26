#!/usr/bin/python3
import os
import struct
import subprocess
import tempfile
import tkinter as tk

BARS_NUMBER = 256
# OUTPUT_BIT_FORMAT = "8bit"
OUTPUT_BIT_FORMAT = "16bit"
# RAW_TARGET = "/tmp/cava.fifo"
RAW_TARGET = "/dev/stdout"

conpat = """
[general]
bars = %d
[output]
method = raw
raw_target = %s
bit_format = %s
"""

config = conpat % (BARS_NUMBER, RAW_TARGET, OUTPUT_BIT_FORMAT)
bytetype, bytesize, bytenorm = ("H", 2, 65535) if OUTPUT_BIT_FORMAT == "16bit" else ("B", 1, 255)


def run():
    # Create the main window
    window = tk.Tk()
    window.title("Simple GUI for Cava")
    bar = tk.Canvas(window, width=800,height=600)
    bar.pack()

    with tempfile.NamedTemporaryFile() as config_file:
        config_file.write(config.encode())
        config_file.flush()

        process = subprocess.Popen(["cava", "-p", config_file.name], stdout=subprocess.PIPE)
        chunk = bytesize * BARS_NUMBER
        fmt = bytetype * BARS_NUMBER

        if RAW_TARGET != "/dev/stdout":
            if not os.path.exists(RAW_TARGET):
                os.mkfifo(RAW_TARGET)
            source = open(RAW_TARGET, "rb")
        else:
            source = process.stdout

        def loop():
            data = source.read(chunk)
            if len(data) < chunk:
                return
            # sample = [i for i in struct.unpack(fmt, data)]  # raw values without norming
            sample = [i / bytenorm for i in struct.unpack(fmt, data)]
            i = 0
            w = 800 / BARS_NUMBER
            bar.delete("all")
            for v in sample:
                bar.create_rectangle(i*w,600-v*600,i*w+w,600,fill='green', outline='green')
                i+=1
            window.after(10, loop)
        # Set the window to be always on top
        window.wm_attributes("-topmost", True)
        window.after(20, loop)
        window.mainloop()
        

if __name__ == "__main__":
    run()
