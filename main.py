import pyaudio
import sounddevice as sd
import numpy as np
import tkinter as tk
import threading
import time

input_device = 4
output_device = 16
sample_rate = 44100  # Sample rate in Hz
buffer_size = 1024  # Size of the audio buffer

pa_format = pyaudio.paInt16
np_format = np.int16
max_format = 32767

p = pyaudio.PyAudio()

stream = p.open(
    format=pa_format,
    channels=2,
    rate=sample_rate,
    input=True,
    output=False,
    frames_per_buffer=buffer_size,
    input_device_index=input_device,
    stream_callback=None
)

output_stream = sd.OutputStream(
    samplerate=sample_rate,
    channels=2,
    dtype=np_format,
    latency='low',
    device=output_device
)

stream.start_stream()
output_stream.start()

# Tkinter setup
window = tk.Tk()
canvas = tk.Canvas(window, bg="white", height=480, width=720)
canvas.pack()

# Handle window close
def on_closing():
    close = True
    T1.join()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)

def getAudioData():
    # Read audio data from input stream
    input_data = stream.read(buffer_size, exception_on_overflow=False)
    
    # Convert input data to numpy array
    data = np.frombuffer(input_data, dtype=np_format)
    
    # Reshape the data into a two-dimensional array with shape (buffer_size, 2)
    data = data.reshape(-1, 2)

    return data

def audio_frame(_data):
    # Create a copy of the array to make it writable
    data_copy = np.copy(_data)
    
    data_copy[:, 0] = data_copy[:, 0]  # Left channel
    data_copy[:, 1] = data_copy[:, 1]  # Right channel
    
    # Play the processed audio through VB-Audio Cable
    output_stream.write(data_copy)

def canvas_frame(_data):
    canvas.delete("all")

    height = 480
    width = 720
    sample = 1
    points = []

    for i in range(0, buffer_size, sample):
        y = _data[i, 0] / max_format * height / 2 + height / 2
        x = i * sample / buffer_size * width
        points.append(x)
        points.append(y)

    canvas.create_line(points)
    window.update()

data = getAudioData()
close = False

def processAudio():
    while not close:
        global data
        data = getAudioData()
        audio_frame(data)

T1 = threading.Thread(target=processAudio)
T1.start()

# TODO:
# - Making adjustable volume by graph
# - Making adjustable frequency offset
# - Making noise gate
# - Making auto volume scaling based on max over time increase / decrease (if higher above threshold, faster decrease max)

# - Making so that it doesnt fuck up discord on launch

try:
    while True:
        canvas_frame(data)
        time.sleep(0.01)
except KeyboardInterrupt:
    close = True
    T1.join()