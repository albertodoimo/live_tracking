#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created: 2026-1-8
Author: Alberto Doimo
email: alberto.doimo@uni-konstanz.de

Description
-----------
Generates and saves a single ArUco marker image with a specified ID.

"""
##############################################################################
# Libraries import
##############################################################################

import os
import cv2
from cv2 import aruco
import matplotlib.pyplot as plt

##############################################################################
# Generate and save marker
##############################################################################
os.chdir(os.path.dirname(os.path.abspath(__file__)))

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
marker_ID = 200

marker_image = aruco.generateImageMarker(aruco_dict, marker_ID, 220, 1)

# Save and display the marker
cv2.imwrite(f"marker_{marker_ID}.png", marker_image)
plt.imshow(marker_image, cmap="gray")
plt.show()
