Installation
============

Hardware
--------

* Multichannel Usb Audio interface (currently `RME 802 <https://rme-audio.de/de_fireface-802.html>`_)
* Ceiling Camera: `Basler ace2 R a2A4508-20umBAS <https://docs.baslerweb.com/a2a4508-20umbas>`_ 
* Desktop or Laptop computer with USB ports.
* Printed `Aruco Markers <https://docs.opencv.org/3.4/d5/dae/tutorial_aruco_detection.html>`_ for tracking (at least 10x10 cm markers for good detection at ~3m distance.)


Software
--------

Thanks to `OpenCV <https://docs.opencv.org/3.4/index.html>`_ and `pypylon <https://www.baslerweb.com/en/software/pylon/pypylon/>`_ libraries this is a fully open source and free tracking. 
Install the required packages:
   
    .. code-block:: shell
    
        pip install -r requirements.txt

Setup
-----

1. Connect the audio interface to the computer via USB.
2. Connect ceiling camera to the computer via USB.
3. Connect the loudspeaker to the audio interface output.
4. Connect proprietary cable from camera to the audio interface to trigger the camera frames from the soundcard.
5. Place the Aruco markers in the corners of the tracking area and make sure they are visible from the ceiling camera.
6. Place the Aruco markers on the robots to be tracked and make sure they are visible from the ceiling camera.




