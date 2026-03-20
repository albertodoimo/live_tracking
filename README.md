# live_tracking

This repository contains code and resources for a live tracking of real-time robots in the lab using a Basler camera and ArUco markers.

## Files

`hardware_trigger_and_store_frames.py`: Python script to trigger the Basler camera using hardware trigger and store the captured frames at a specific rate. Frames are triggered by `audio_repr_sounddevice.py` from lab PC with a soundcard outputting the trigering signal.

`live_video_tracking_basler.py`: Python script to perform live video tracking of robots using a Basler camera and ArUco markers. The script displays frames from the camera, with detected ArUco markers, and tracks their positions in real-time.

## Requirements

```
opencv-contrib-python==4.10.0.84
opencv-python==4.10.0.84
pypylon==4.2.0
scipy==1.15.3
sounddevice==0.4.7
soundfile==0.12.1
numpy==1.26.4
```
https://pypi.org/project/pypylon/ 

https://pypi.org/project/opencv-python/
