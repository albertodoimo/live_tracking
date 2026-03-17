#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created: 2025-11-12
Author: Alberto Doimo
email: alberto.doimo@uni-konstanz.de

Description
-----------
Audio reproduction of camera+sync signal and target localization/repulsion signal from sounddevice

"""
###############################################################################
# Libraries import
###############################################################################

import sounddevice as sd
import numpy as np
import soundfile as sf
from datetime import datetime
import time
from scipy import signal

###############################################################################
# SETUP PARAMETERS
###############################################################################

# Load wav files

# List available audio devices
print("Available audio devices:")
print(sd.query_devices())

# Select your device by index (change this number based on the list above)
device_index = 20
print("\ndevice_samplerate:", sd.query_devices(device_index)["default_samplerate"])

# Load the stereo wav file for channels 1-2
tracking_signal, fs1 = sf.read("15_Hz_tracking_sync_signal_48000.wav")

multich_signal, fs2 = sf.read("multich-1000_chirp_100-4000hz_48khz.wav")

print(f"tracking_signal shape: {tracking_signal.shape}, fs1: {fs1}")
print(f"multich_signal shape: {multich_signal.shape}, fs2: {fs2}")


if fs1 != fs2:
    # Resample multich_signal to match fs1
    if fs1 < fs2:
        print(f"Resampling from {fs2} Hz to {fs1} Hz ...")
        multich_signal = signal.resample(
            multich_signal, int(len(multich_signal) * fs1 / fs2)
        )
    else:
        print(f"Resampling from {fs1} Hz to {fs2} Hz ...")
        tracking_signal = signal.resample(
            tracking_signal, int(len(tracking_signal) * fs2 / fs1)
        )

# Find the maximum length to pad correctly
len_track = tracking_signal.shape[0]
len_multi = multich_signal.shape[0]
# print(f"Original lengths: tracking_signal={len_track}, multich_signal={len_multi}")
max_len = max(len_track, len_multi)

# Pad ONLY the time axis (axis 0), adding zeros to the end. (axis 1 gets 0 padding)
track_padded = np.pad(
    tracking_signal, ((0, max_len - len_track), (0, 0)), mode="constant"
)
multi_padded = np.pad(
    multich_signal, ((0, max_len - len_multi), (0, 0)), mode="constant"
)

# Use hstack now that they are strict columns: shape becomes (Samples, Total_Channels)
output_sig = np.float32(np.hstack([track_padded, multi_padded]))
print("output_sig shape", output_sig.shape)

# Save the combined output signal to a wav file
output_filename = "combined_output.wav"
sf.write(output_filename, output_sig, fs1)
print(f"Output signal saved to: {output_filename}")

# ---- PLAYBACK WITH CTRL-C INTERRUPT ----
print(f"\nPlaying audio on device:\n {sd.query_devices(device_index)['name']}\n")
for i in range(3, 0, -1):
    print(f"Starting in {i} seconds... \n")
    time.sleep(1)
sd.play(output_sig, samplerate=fs1, device=device_index)

for i in range(1, 30 * 60):
    time.sleep(1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    minutes = ((i * 1) % 3600) // 60
    seconds = (i * 1) % 60
    print(f"Time: {minutes:02d}m {seconds:02d}s")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopping playback...")
    sd.stop()

print("Playback stopped by user.")
