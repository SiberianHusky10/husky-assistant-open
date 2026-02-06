import pyaudio
import numpy as np

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=1024
)

print("🎤 listening...")
while True:
    data = stream.read(1024, exception_on_overflow=False)
    audio = np.frombuffer(data, dtype=np.int16)
    volume = int(abs(audio).mean())
    print(volume)
