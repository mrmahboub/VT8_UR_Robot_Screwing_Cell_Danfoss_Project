import os
import wave
import pyaudio
import time

# Parameters
record_time = 600  # Record for 10 minutes (600 seconds)
output_folder = r'C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Data\Audio data\Noise'
output_file = "Noise uden luft (21-06-2025).wav"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Set up pyaudio
chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 44100

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open a stream for recording
stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

# Start recording
print("Recording...")

frames = []

start_time = time.time()
while time.time() - start_time < record_time:
    data = stream.read(chunk)
    frames.append(data)

# Stop recording
print("Recording finished.")
stream.stop_stream()
stream.close()
audio.terminate()

# Save the recorded audio
output_path = os.path.join(output_folder, output_file)
with wave.open(output_path, 'wb') as wf:
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))

print(f"Audio saved to: {output_path}")