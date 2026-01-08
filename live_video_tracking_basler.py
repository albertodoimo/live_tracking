#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created: 2025-12-19
Author: Alberto Doimo
email: alberto.doimo@uni-konstanz.de

Description:

Live video tracking using Basler camera and ArUco markers.
Assumes each robot is marked with two ArUco markers to avoid lost tracking.
Uses pypylon for camera interfacing and OpenCV for image processing with Aruco markers for robot detection.

Notes:
    camera model = ace2 R a2A4508-20umBAS

"""
#############################################################################
# Libraries import
#############################################################################

from pypylon import pylon
import cv2
import numpy as np
import yaml
import datetime
import queue
import time
from utilities_tracking import *

###############################################################################
# SETUP PARAMETERS
###############################################################################

# Specify the path to your YAML file
yaml_file = "./camera_calibration/calibration_matrix_basler_2560-1600.yaml"

# Load camera calibration data from YAML file
try:
    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file)
        camera_matrix = np.array(data["camera_matrix"])
        dist_coeffs = np.array(data["dist_coeff"])
except FileNotFoundError:
    print(f"Error: The file '{yaml_file}' does not exist.")
except yaml.YAMLError as exc:
    print("Error parsing YAML file:", exc)

# Setup the camera
# camera model = ace2 R a2A4508-20umBAS
tl_factory = pylon.TlFactory.GetInstance()
devices = tl_factory.EnumerateDevices()
if not devices:
    print("No Basler camera found.")
camera = pylon.InstantCamera(tl_factory.CreateDevice(devices[0]))
camera.Open()

# Set camera parameters
# Original image size
original_width = 4504
original_height = 4096
# Crop size
crop_w = 2560
crop_h = 1600

# Define marker pairs and robot names
marker_pairs = [(4, 5), (6, 7), (10, 11)]
robot_names = {(4, 5): "241", (6, 7): "240", (10, 11): "238"}

# Arena dimensions in meters from the marks on the carpet
print("------------------- Check arena dimensions! ---------------------")
arena_w = 1.47  # m
arena_l = 1.91  # m
camera.Width.SetValue(crop_w)
camera.Height.SetValue(crop_h)

# Center crop into the original image
camera.BslCenterX.Execute()
camera.BslCenterY.Execute()
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

# Convert Basler images to OpenCV format
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

# Load ArUco dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
aruco_params = cv2.aruco.DetectorParameters()

# Get and print the camera's frame rate
camera_fps = camera.ResultingFrameRate.GetValue()
print(f"\nHardware Camera FPS output: {camera_fps}")

# Get the current camera temperature
print(f"\nTemperature: {camera.DeviceTemperature.Value}")

# Set the upper limit of the camera's frame rate
camera.AcquisitionFrameRateEnable.Value = True
camera.AcquisitionFrameRate.Value = 35

# Determine the sensor readout time at the current settings
readout_time = camera.SensorReadoutTime.Value
print(f"\nReadout time: {readout_time}")

# Determine the sensor readout time at the current settings
exposure_time = camera.ExposureTime.Value
print(f"\nExposure time: {exposure_time}")

# Determine the sensor readout time at the current settings
eff_exposure_time = camera.BslEffectiveExposureTime.Value
print(f"\nEffective exposure time: {eff_exposure_time}")

# Calculate arena dimensions
try:
    pixel_per_meters = 0
    camera.TimestampLatch.Execute()
    while camera.IsGrabbing():
        grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grab_result.GrabSucceeded():
            image = converter.Convert(grab_result)
            frame = image.GetArray()
            h, w = frame.shape[:2]

            if "mapx" not in locals():
                new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
                    camera_matrix, dist_coeffs, (w, h), 1, (w, h)
                )
                mapx, mapy = cv2.initUndistortRectifyMap(
                    camera_matrix,
                    dist_coeffs,
                    None,
                    new_camera_matrix,
                    (w, h),
                    cv2.CV_16SC2,
                )

            undistorted = cv2.remap(frame, mapx, mapy, interpolation=cv2.INTER_LINEAR)

            corners, ids, _ = cv2.aruco.detectMarkers(
                frame, aruco_dict, parameters=aruco_params
            )

            # Draw detected markers
            if ids is not None:
                corners_array = np.squeeze(np.array(corners))
                try:
                    ind1 = np.where(ids == 1)[0]
                    if len(ind1) == 0:
                        raise ValueError("Marker 0 not found")
                    ind2 = np.where(ids == 2)[0]
                    if len(ind2) == 0:
                        raise ValueError("Marker 1 not found")
                    ind3 = np.where(ids == 3)[0]
                    if len(ind3) == 0:
                        raise ValueError("Marker 2 not found")
                    # bottom left of 1, top left of 2, top right of 3
                    corners_1 = corners_array[ind1]
                    corners_2 = corners_array[ind2]
                    reference_position = corners_2[:, 2][
                        0
                    ]  # Use the bottom right corner of marker 2 as reference
                    print(
                        f"Reference: {reference_position}, type: {type(reference_position)}"
                    )
                    corners_3 = corners_array[ind3]
                    pixel_per_meters = np.mean(
                        [
                            np.linalg.norm(corners_1[:, 3] - corners_2[:, 0], axis=1)
                            / arena_w,
                            np.linalg.norm(corners_2[:, 0] - corners_3[:, 1], axis=1)
                            / arena_l,
                        ]
                    )
                    print("Pixel per meters: %.2f" % pixel_per_meters)
                except ValueError:
                    print("Corner Marker 0, 1 or 2 not found")
            if pixel_per_meters > 0:
                break
            grab_result.Release()
except Exception as e:
    print(f"Error calculating pixel per meters: {e}")


if __name__ == "__main__":

    try:
        while camera.IsGrabbing():
            # Get the latest image from the camera
            grab_result = camera.RetrieveResult(
                5000, pylon.TimeoutHandling_ThrowException
            )

            if grab_result.GrabSucceeded():
                timestamp = str(
                    datetime.datetime.timestamp(
                        datetime.datetime.now(datetime.timezone.utc)
                    )
                    - readout_time
                )

                # Convert the grabbed image to OpenCV format
                image = converter.Convert(grab_result)
                frame = image.GetArray()
                original_frame = frame.copy()
                h, w = frame.shape[:2]

                # Detect Markers
                corners, ids, _ = cv2.aruco.detectMarkers(
                    frame, aruco_dict, parameters=aruco_params
                )
                print("\nIDS", np.sort(ids.flatten()) if ids is not None else [])

                marker_centers = get_marker_centers(corners, ids)
                id_list = ids.flatten().tolist() if ids is not None else []
                centers_dict = {
                    id_: center for id_, center in zip(id_list, marker_centers)
                }

                # Draw axes on the video to indicate increasing X (right) and Y (down) directions from origin
                axis_length = 100  # pixels
                # X axis: right from reference_position
                x_axis_end = (
                    int(reference_position[0] + axis_length),
                    int(reference_position[1]),
                )

                # Y axis: down from reference_position
                y_axis_end = (
                    int(reference_position[0]),
                    int(reference_position[1] + axis_length),
                )

                # Draw X axis (red)
                cv2.arrowedLine(
                    frame,
                    tuple(reference_position.astype(int)),
                    x_axis_end,
                    (0, 0, 255),
                    4,
                    tipLength=0.2,
                )
                cv2.putText(
                    frame,
                    "X",
                    (x_axis_end[0] + 10, x_axis_end[1]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

                # Draw Y axis (green)
                cv2.arrowedLine(
                    frame,
                    tuple(reference_position.astype(int)),
                    y_axis_end,
                    (0, 0, 255),
                    4,
                    tipLength=0.2,
                )
                cv2.putText(
                    frame,
                    "Y",
                    (y_axis_end[0], y_axis_end[1] + 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

                pair_centers = get_pair_centers(
                    marker_pairs,
                    centers_dict,
                    corners,
                    ids,
                    reference_position,
                    pixel_per_meters,
                )
                heading_vectors, pixel_centers, heading_angle = draw_heading_arrows(
                    frame,
                    pair_centers,
                    robot_names,
                    corners,
                    ids,
                    reference_position,
                    pixel_per_meters,
                )
                closest_robot_angle = draw_heading_angles(
                    frame, heading_vectors, pixel_centers, robot_names
                )
                draw_pair_centers(
                    frame,
                    pair_centers,
                    robot_names,
                    reference_position,
                    pixel_per_meters,
                )
                intradistances = draw_closest_pair_line(
                    frame,
                    pair_centers,
                    robot_names,
                    reference_position,
                    pixel_per_meters,
                )

                text_size, _ = cv2.getTextSize(
                    timestamp, cv2.FONT_HERSHEY_SIMPLEX, 1, 2
                )
                text_x = (frame.shape[1] - text_size[0]) // 2
                text_y = 40
                cv2.putText(
                    frame,
                    timestamp,
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.3,
                    (0, 0, 0),
                    3,
                    cv2.LINE_AA,
                )

                cv2.namedWindow("Basler Camera tracking", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Basler Camera tracking", 1600, 1200)

                # Show the camera window
                cv2.imshow("Basler Camera tracking", frame)

                # # Show the original camera feed
                # cv2.namedWindow("Basler Camera original", cv2.WINDOW_NORMAL)
                # cv2.resizeWindow("Basler Camera original", 1600, 1200)
                # cv2.imshow("Basler Camera original", original_frame)

                # Stop recording and save data when ESC is pressed or window is closed
                if (
                    cv2.waitKey(1) & 0xFF == 27
                    or cv2.getWindowProperty(
                        "Basler Camera tracking", cv2.WND_PROP_VISIBLE
                    )
                    < 1
                ):
                    break

            grab_result.Release()
    finally:
        camera.StopGrabbing()
        camera.Close()
        cv2.destroyAllWindows()
