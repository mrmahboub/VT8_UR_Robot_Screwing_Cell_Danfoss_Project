import librosa
import numpy as np
from scipy.signal import butter, lfilter
import soundfile as sf

# Define the audio files
ten_min_audio_files = [
    r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Data\Audio data\Noise\Noise (19-05-2025).wav",
    r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Data\Audio data\Noise\Noise (20-05-2025).wav",
    r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Data\Audio data\Noise\Noise (21-06-2025).wav",
    r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Data\Audio data\Noise\Noise uden luft (21-06-2025).wav"
    ]

def low_pass_filter(cutoff_freq, sample_rate, order=0.5):
    nyq = 0.5 * sample_rate
    normalized_cutoff = cutoff_freq / nyq
    b, a = butter(order, normalized_cutoff, btype='low', analog=False)
    return b, a

def apply_filter(data, cutoff_freq, sample_rate, order=1):
    b, a = low_pass_filter(cutoff_freq, sample_rate, order=order)
    filtered_data = lfilter(b, a, data)
    return filtered_data

# Initialize a variable to hold the sum of the frequency ranges
sum_freq_ranges = 0

for audio_file in ten_min_audio_files:
    # Load the 10-minute audio file
    ten_min_audio, sr = librosa.load(audio_file, sr=None)

    # Calculate the short-time Fourier transform (STFT) to get frequency information
    ten_min_stft = np.abs(librosa.stft(ten_min_audio))

    # Calculate the average frequency range
    avg_freq_range = np.mean(ten_min_stft, axis=1)

    # Add the average frequency range to the sum
    sum_freq_ranges += avg_freq_range

# Calculate the overall average frequency range
avg_freq_range_overall = sum_freq_ranges / len(ten_min_audio_files)

# Determine the cutoff frequency based on the average frequency range
cutoff_freq = np.argmax(avg_freq_range_overall)

# Load the 4-second audio file
four_sec_audio_file = r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Data\Audio data\Noise reduction\sample with noise.wav"
four_sec_audio, sr = librosa.load(four_sec_audio_file, sr=None)

# Apply the low-pass filter
filtered_audio = apply_filter(four_sec_audio, cutoff_freq, sr)

# Save the filtered audio file
sf.write(r"C:\Users\AMRAN\OneDrive - Aalborg Universitet\8. semester\Projekt\CODE\Data\Audio data\Noise reduction\sample without noise.wav", filtered_audio, sr)




