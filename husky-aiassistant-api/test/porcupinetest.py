import pvporcupine
import pyaudio
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

porcupine = pvporcupine.create(
    access_key=os.getenv("PICOVOICE_ACCESS_KEY"),
    keywords=["porcupine"])
pa = pyaudio.PyAudio()

stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("🎧 say 'porcupine'")

while True:
    pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
    pcm = np.frombuffer(pcm, dtype=np.int16)

    if porcupine.process(pcm) >= 0:
        print("🟢 detected")
