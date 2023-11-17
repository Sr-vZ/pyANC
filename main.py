import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
import time
from tkinter import TclError

# Constants
CHUNK = 1024 * 2  # Samples per frame
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Single channel for microphone
RATE = 44100  # Samples per second

# Create matplotlib figure and axes for the original sound
fig, (ax_original, ax_antimirror) = plt.subplots(1, 2, figsize=(15, 7))
ax_original.axhline(y=128, linestyle="--", color="gray")
ax_original.set_title("Original Sound")
ax_original.set_xlabel("samples")
ax_original.set_ylabel("amplitude")
ax_original.set_ylim(0, 255)
ax_original.set_xlim(0, 2 * CHUNK)
plt.setp(ax_original, xticks=[], yticks=[])

# Create matplotlib figure and axes for the antisound
ax_antimirror.axhline(y=128, linestyle="--", color="gray")
ax_antimirror.set_title("Antisound")
ax_antimirror.set_xlabel("samples")
ax_antimirror.set_ylabel("amplitude")
ax_antimirror.set_ylim(0, 255)
ax_antimirror.set_xlim(0, 2 * CHUNK)
plt.setp(ax_antimirror, xticks=[], yticks=[])

# PyAudio class instance
p = pyaudio.PyAudio()

# Stream object to get data from microphone
inputstream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK,
)

# Stream object to output antisound
outputstream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK,
)

# Variable for plotting
x = np.arange(0, 2 * CHUNK, 2)

# Create a line object with random data for original sound
(line_original,) = ax_original.plot(
    x, np.random.rand(CHUNK), "-", lw=1, mec=(255, 0, 0, 1)
)

# Create a line object with random data for antisound
(line_antimirror,) = ax_antimirror.plot(
    x, np.random.rand(CHUNK), "-", lw=1, mec=(0, 0, 255, 1)
)

# Basic formatting for the axes

# Show the plot
plt.show(block=False)

print("stream started")

# For measuring frame rate
frame_count = 0
start_time = time.time()

while True:
    # Binary input data
    data = inputstream.read(CHUNK)

    # Convert data to integers
    data_int = struct.unpack(str(2 * CHUNK) + "B", data)

    # Convert data to np array and offset by 128
    data_np = np.array(data_int, dtype="b")[::2] + 128

    # Create array of anti sound
    data_np_mirror = 128 - (data_np - 128)

    # Convert antisound to integer list to output
    data_int_mirror = (data_np_mirror - 128).tolist()

    # Convert antisound to binary
    data_mirror = struct.pack(str(CHUNK) + "h", *data_int_mirror)

    # Output antisound
    outputstream.write(data_mirror)

    line_original.set_ydata(data_np)
    line_antimirror.set_ydata(data_np_mirror)

    # Update figure canvas
    try:
        fig.canvas.draw()
        fig.canvas.flush_events()
        frame_count += 1

    except TclError:
        # Calculate average frame rate
        frame_rate = frame_count / (time.time() - start_time)

        print("stream stopped")
        print("average frame rate = {:.0f} FPS".format(frame_rate))
        break
