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

###############################################################################
# SETUP PARAMETERS
###############################################################################

# Load wav files

# List available audio devices
print("Available audio devices:")
print(sd.query_devices())

# Select your device by index (change this number based on the list above)
device_index = 20
print('\ndevice_samplerate:', sd.query_devices(device_index)['default_samplerate'])

# Load the stereo wav file for channels 1-2
tracking_signal, fs1 = sf.read('15_Hz_tracking_sync_signal_48000.wav')
print(fs1)

# ---- PLAYBACK WITH CTRL-C INTERRUPT ----
print(f"\nPlaying audio on device:\n {sd.query_devices(device_index)['name']}\n")
for i in range(3, 0, -1):
    print(f"Starting in {i} seconds... \n")
    time.sleep(1)
sd.play(tracking_signal, samplerate=fs1, device=device_index)
print("Playback running... Press CTRL+C to stop.")
for i in range(1, 30*60):
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