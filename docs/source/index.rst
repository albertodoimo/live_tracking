Welcome to **live_tracking**'s documentation!
=============================================

**live_tracking** is designed for real-time tracking of acoustic agents in a swarm. It provides tools for recording video frames for precise time syncronization and localization of the robots. Raw data can be further analysed with `SwarmTracking <https://github.com/activesensingcollectives/SwarmTracking>`_ repository. 

Overview
--------
.. raw:: html

   <video width="100%" loop controls>
     <source src="_static/2025-10-02_18-45-28_upsampled_2.mp4" type="video/mp4">
   </video>

Tracking acoustic objects in a swarm is challenging due to the need for precise time synchronization.
**live_tracking** and **SwarmTracking** addresses these challenges by providing tools for processing video and audio data, enabling precise time syncronization of the robots.
Hardware integration allows to trigger the camera frames from a soundcard by using a square wave signal at a specific framerate. At the same time a loudspeaker reproduces a sync signal sound that is recorded from all the robots and aligns the audio in the post-processing analysis.


Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Installation:

   installation.rst

.. toctree::
   :maxdepth: 2
   :caption: Usage:
   
   usage.rst

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api.rst

Documentation Authors
-----------------------
- Alberto Doimo (`Github <https://github.com/albertodoimo>`_)
- Allen Binu 

Links
-----

Publications using live_tracking:

   `Doimo, A., Hamann, H., Reina, A., & Beleyur, T. (2026). SonoRo: A swarm robotics platform to study acoustically driven collective behaviour (in press). ANTS 2026. <https://www.giovannireina.com/pdf/Doimo-ANTS-2026.pdf>`_


   If you use this project or find our paper useful, please cite it using the following format:

   **Plain Text / APA:**

   Doimo, A., Hamann, H., Reina, A., & Beleyur, T. (2026). SonoRo: A swarm robotics platform to study acoustically driven collective behaviour (in press). ANTS 2026.

   **BibTeX:**

   .. code-block:: bibtex


      @inCollection{Doimo:ANTS:2026,
         author = {Doimo, Alberto and Hamann, Heiko and Reina, Andreagiovanni and Beleyur, Thejasvi},
         title = {Sono{R}o: A Swarm Robotics Platform to Study Acoustically-Driven Collective Behaviour},
         address = {Cham},
         doi={},
         pages = {in press},
         series = {LNCS},
         volume = {16515},
         editor = {{R. Gross et al.}},
         booktitle = {Swarm Intelligence (ANTS 2026)},
         publisher = {Springer},
         year = {2026}
      }

   .. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.17664282.svg
      :target: https://doi.org/10.5281/zenodo.17664282


Active Sensing Collectives Lab:

- `Github <https://github.com/activesensingcollectives>`_
- `Website <https://www.activesensingcollectives.com/>`_


Funding
-------

- Carl-Zeiss-Stiftung 
- Deutsche Forschungsgemeinschaft (DFG) under Germany’s Excellence Strategy – EXC 2117-422037984
- DFG’s Walter Benjamin program - 502056951

License
-------

MIT License

Copyright (c) 2026 Alberto Doimo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.