#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created: 2025-12-19
Author: Alberto Doimo
email: alberto.doimo@uni-konstanz.de

Description:

Utilities for tracking ArUco markers and calculating robot positions and headings.

"""
import cv2
import numpy as np


def get_marker_centers(corners, ids):
    """Get the center coordinates of each detected ArUco marker.

    Parameters
    ----------
    corners : list
        List of detected marker corners from cv2.aruco.detectMarkers.
    ids : list
        List of detected marker IDs from cv2.aruco.detectMarkers.

    Returns
    -------
    marker_centers : list
        A list of (x, y) tuples representing the center of each marker.

    """
    marker_centers = []
    if ids is not None:
        for marker_corners in corners:
            pts = marker_corners[0]
            center_x = int(np.mean(pts[:, 0]))
            center_y = int(np.mean(pts[:, 1]))
            marker_centers.append((center_x, center_y))
    return marker_centers


def get_pair_centers(
    marker_pairs, centers_dict, corners, ids, reference_position, pixel_per_meters
):
    """Calculate the centers of marker pairs, with optional relative positioning.

    This function computes the center point for each pair of markers. If both markers
    are detected, the center is the midpoint. If only one marker is detected, the center
    is placed 5 cm away from that marker in a direction parallel to the marker's edge.
    Centers can be returned in pixel coordinates or relative to a reference position.

    Parameters
    ----------
    marker_pairs : list of tuple
        List of (a, b) tuples representing marker pairs to process.
    centers_dict : dict
        Dictionary mapping marker IDs to their center coordinates as (x, y) tuples.
    corners : ndarray
        Array of corner coordinates for detected markers.
    ids : ndarray or None
        Array of detected marker IDs, shape (n, 1).
    reference_position : tuple or None
        Reference position (x, y) for computing relative coordinates.
    pixel_per_meters : float
        Conversion factor from meters to pixels.

    Returns
    -------
    dict
        Dictionary mapping marker pairs (a, b) to their center coordinates.

    Notes
    -----
    - If both markers in a pair are in centers_dict, the center is their midpoint.
    - If only marker a is available, the center is placed 5 cm to the right
      (parallel to the marker's edge defined by corners 0-1).
    - If only marker b is available, the center is placed 5 cm to the left
      (parallel to the marker's edge).
    - Pairs where neither marker is available are skipped.

    """
    pair_centers = {}
    id_list = ids.flatten().tolist() if ids is not None else []
    for a, b in marker_pairs:
        if a in centers_dict and b in centers_dict:
            x = int((centers_dict[a][0] + centers_dict[b][0]) / 2)
            y = int((centers_dict[a][1] + centers_dict[b][1]) / 2)
            center = (x, y)
        elif a in centers_dict and a in id_list and pixel_per_meters > 0:
            # Place center 5 cm to the right of marker a, parallel to corners 0-1
            a_idx = id_list.index(a)
            a_corners = corners[a_idx][0]
            vec = a_corners[1] - a_corners[0]
            vec = vec / np.linalg.norm(vec)
            shift = vec * (pixel_per_meters * 0.05)  # 5 cm to the right
            x = int(centers_dict[a][0] + shift[0])
            y = int(centers_dict[a][1] + shift[1])
            center = (x, y)
        elif b in centers_dict and b in id_list and pixel_per_meters > 0:
            # Place center 5 cm to the left of marker b, parallel to corners 0-1
            b_idx = id_list.index(b)
            b_corners = corners[b_idx][0]
            vec = b_corners[1] - b_corners[0]
            vec = vec / np.linalg.norm(vec)
            shift = -vec * (pixel_per_meters * 0.05)  # 5 cm to the left
            x = int(centers_dict[b][0] + shift[0])
            y = int(centers_dict[b][1] + shift[1])
            center = (x, y)
        else:
            continue
        if reference_position is not None and pixel_per_meters > 0:
            rel_center = (
                (center[0] - reference_position[0]) / pixel_per_meters,
                (center[1] - reference_position[1]) / pixel_per_meters,
            )
            pair_centers[(a, b)] = rel_center
        else:
            pair_centers[(a, b)] = center
    return pair_centers


def draw_heading_arrows(
    frame, pair_centers, robot_names, corners, ids, reference_position, pixel_per_meters
):
    """Draw heading arrows on a frame based on marker positions and orientations.

    This function visualizes the heading direction of robots by drawing arrows
    on the input frame. The heading direction is determined from ArUco marker
    corners, and arrows are scaled and positioned based on reference coordinates
    and pixel-to-meter conversion factors.

    Parameters
    ----------
    frame : np.ndarray
        The video frame (image) on which to draw the heading arrows.
    pair_centers : dict
        Dictionary mapping marker pairs (a, b) to their center coordinates
        in world coordinates (meters).
    robot_names : dict
        Dictionary mapping marker pairs (a, b) to robot names (Raspberry Pi last IP number).
    corners : ndarray
        Array of corner coordinates for detected markers.
    ids : ndarray or None
        Array of detected marker IDs, shape (n, 1).
    reference_position : tuple or np.ndarray, optional
        Reference position (x, y) for computing relative coordinates.
    pixel_per_meters : float
        Conversion factor from meters to pixels.

    Returns
    -------
    heading_vectors : dict
        Dictionary mapping marker pairs (a, b) to normalized heading direction
        vectors in 2D space.
    pixel_centers : dict
        Dictionary mapping marker pairs (a, b) to their pixel coordinates referred to the reference position
    heading_angle : dict
        Dictionary mapping robot names to heading angles in degrees, where
        0° is vertical (top) and angles increase clockwise (0-360°).

    Notes
    -----
    - Heading vectors are computed from ArUco marker corners (pt0 - pt3).
    - Arrows are drawn with a fixed length of 100 pixels.

    """
    heading_vectors = {}
    pixel_centers = {}
    id_list = ids.flatten().tolist() if ids is not None else []
    for (a, b), center in pair_centers.items():
        heading_vec = None
        arrow_start = None

        # Try to get heading from marker a
        if a in id_list:
            a_idx = id_list.index(a)
            a_corners = corners[a_idx][0]
            pt0 = a_corners[0]
            pt3 = a_corners[3]
            heading_vec = pt0 - pt3
        # If marker a not found, try marker b
        elif b in id_list:
            b_idx = id_list.index(b)
            b_corners = corners[b_idx][0]
            pt0 = b_corners[0]
            pt3 = b_corners[3]
            heading_vec = pt0 - pt3

        if heading_vec is not None:
            heading_vec = heading_vec / np.linalg.norm(heading_vec)
            heading_vectors[(a, b)] = heading_vec
            if reference_position is not None and pixel_per_meters > 0:
                arrow_start = np.array(
                    [
                        int(reference_position[0] + center[0] * pixel_per_meters),
                        int(reference_position[1] + center[1] * pixel_per_meters),
                    ]
                )
            else:
                arrow_start = np.array(center)
            arrow_length = 100
            arrow_end = arrow_start + heading_vec * arrow_length

            # Heading angle: 0 deg is vertical (facing top), increases clockwise (0-360)
            heading_angle_rad = np.arctan2(
                heading_vec[1], heading_vec[0]
            )  # negative y for top
            heading_angle_deg = (
                np.degrees(heading_angle_rad) + 90
            ) % 360  # 0 deg is top
            if "heading_angle" not in locals():
                heading_angle = {}
            robot_name = (
                robot_names.get((a, b), f"{a}-{b}")
                if "robot_names" in locals()
                else f"{a}-{b}"
            )
            heading_angle[robot_name] = heading_angle_deg

            # cv2.putText(frame, f"{angle_deg:.1f} deg", (arrow_start[0], arrow_start[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.arrowedLine(
                frame,
                tuple(arrow_start.astype(int)),
                tuple(arrow_end.astype(int)),
                (255, 255, 255),
                4,
                tipLength=0.25,
            )
            # cv2.putText(frame, str(heading_vec), (arrow_start[0], arrow_start[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1 )
            pixel_centers[(a, b)] = arrow_start
        else:
            if reference_position is not None and pixel_per_meters > 0:
                pixel_centers[(a, b)] = np.array(
                    [
                        int(reference_position[0] + center[0] * pixel_per_meters),
                        int(reference_position[1] + center[1] * pixel_per_meters),
                    ]
                )
            else:
                pixel_centers[(a, b)] = np.array(center)

    return heading_vectors, pixel_centers, heading_angle


def draw_pair_centers(
    frame, pair_centers, robot_names, reference_position, pixel_per_meters
):
    """Draw marker pair centers on a frame and circle of 100 px around the robot with optional labels.

    Parameters
    ----------
    frame : np.ndarray
        The video frame (image) on which to draw the heading arrows.
    pair_centers : dict
        Dictionary mapping marker pairs (a, b) to their center coordinates
        in world coordinates (meters).
    robot_names : dict, optional
        Dictionary mapping marker pairs (a, b) to robot names (Raspberry Pi last IP number).
    reference_position : tuple or np.ndarray, optional
        Reference position (x, y) for computing relative coordinates.
    pixel_per_meters : float
        Conversion factor from meters to pixels.

    """
    for (a, b), center in pair_centers.items():
        if reference_position is not None and pixel_per_meters > 0:
            draw_center = (
                int(reference_position[0] + center[0] * pixel_per_meters),
                int(reference_position[1] + center[1] * pixel_per_meters),
            )
        else:
            draw_center = center
        # Draw center and distance circles
        # Center circle
        cv2.circle(frame, draw_center, 8, (0, 0, 255), 3)
        # Distance circle
        cv2.circle(frame, draw_center, 100, (255, 255, 255), 2)
        if (a, b) in robot_names:
            if reference_position is not None and pixel_per_meters > 0:
                coord_text = f"({center[0]:.3f}m, {center[1]:.3f}m)"
            else:
                coord_text = f"({draw_center[0]}, {draw_center[1]})"
            cv2.putText(
                frame,
                robot_names[(a, b)],
                (draw_center[0] - 20, draw_center[1] + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
            cv2.putText(
                frame,
                coord_text,
                (draw_center[0] - 20, draw_center[1] + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )


def draw_heading_angles(frame, heading_vectors, pair_centers, robot_names):
    """Draw heading angles and arrows on a frame to visualize the direction to the closest robot.
    This function calculates the angle between each robot's heading vector and the direction
    to its nearest neighboring robot. It draws arrows pointing to the closest robot and
    annotates the angle in degrees on the frame.

    Parameters
    ----------
    frame : np.ndarray
        The video frame (image) on which to draw the heading arrows.
    heading_vectors : dict
        Dictionary mapping marker pairs (a, b) to normalized heading direction
        vectors in 2D space.
    pair_centers : dict
        Dictionary mapping marker pairs (a, b) to their center coordinates
        in world coordinates (meters).
    robot_names : dict
        Dictionary mapping marker pairs (a, b) to robot names (Raspberry Pi last IP number).

    Returns
    -------
    angle_results : dict
        Dictionary mapping robot names to a dictionary containing:
            - 'closest_robot': Name of the closest robot.
            - 'angle_deg': Angle in degrees between the robot's heading and the direction to the closest robot.

    Notes
    -----
    - The function modifies the input frame by drawing arrows and text annotations in place.
    - The angle is calculated as the difference between the direction to the closest robot
      and the robot's heading direction, normalized to the range [0, 360).
    - Arrows are drawn in red (BGR: 0, 0, 255) with a length of 100 pixels.
    - Text annotations displaying the angle are placed 40 pixels to the right and
      20 pixels above the robot's center position.
    """

    angle_results = {}
    for (a, b), heading_vec in heading_vectors.items():
        this_center = np.array(pair_centers[(a, b)])
        min_dist = float("inf")
        closest_center = None
        for (other_a, other_b), other_center in pair_centers.items():
            if (other_a, other_b) == (a, b):
                continue
            dist = np.linalg.norm(this_center - np.array(other_center))
            if dist < min_dist:
                min_dist = dist
                closest_center = np.array(other_center)
                closest_robot = robot_names.get(
                    (other_a, other_b), f"{other_a}-{other_b}"
                )

        closest_robot_angle = None
        if closest_center is not None:
            to_closest = closest_center - this_center
            if np.linalg.norm(to_closest) > 0:
                to_closest_norm = to_closest / np.linalg.norm(to_closest)
                angle_rad = np.arctan2(
                    to_closest_norm[1], to_closest_norm[0]
                ) - np.arctan2(heading_vec[1], heading_vec[0])
                closest_robot_angle = np.degrees(angle_rad) % 360
                text_pos = (int(this_center[0] + 40), int(this_center[1] - 20))
                cv2.putText(
                    frame,
                    f"{closest_robot_angle:.0f} deg",
                    text_pos,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
                # Draw arrow towards closest robot
                arrow_length = 100
                arrow_end = this_center + to_closest_norm * arrow_length
                cv2.arrowedLine(
                    frame,
                    tuple(this_center.astype(int)),
                    tuple(arrow_end.astype(int)),
                    (0, 0, 255),
                    3,
                    tipLength=0.25,
                )
        angle_results[robot_names.get((a, b), f"{a}-{b}")] = {
            "closest_robot": closest_robot,
            "angle_deg": closest_robot_angle,
        }
    return angle_results


def draw_closest_pair_line(
    frame, pair_centers, robot_names, reference_position, pixel_per_meters
):
    """Draw a line between the closest pair of robots and display the distance.

    This function identifies the pair of robots with the minimum distance between them,
    draws a white line connecting them on the frame,
    and displays the distance in millimeters at the midpoint of the line.

    Parameters
    ----------
    frame : np.ndarray
        The video frame (image) on which to draw the heading arrows.
    pair_centers : dict
        Dictionary mapping marker pairs (a, b) to their center coordinates
        in world coordinates (meters).
    robot_names : dict
        Dictionary mapping marker pairs (a, b) to robot names (Raspberry Pi last IP number).
    reference_position : tuple or None
        Reference position (x, y) for computing relative coordinates.
    pixel_per_meters : float
        Conversion factor from meters to pixels.

    Returns
    -------
    list of dict
        List of dictionaries containing pairwise distances.
        Each dictionary has:
        - 'pair': tuple of str, the names of the robot pair
        - 'distance_m': float, the distance between robots in meters

    """
    intradistances = []
    if len(pair_centers) >= 2:
        centers_list = list(pair_centers.values())
        names_list = [
            robot_names.get(pair, f"{pair[0]}-{pair[1]}")
            for pair in pair_centers.keys()
        ]
        min_dist = float("inf")
        closest_pair = (None, None)
        for i in range(len(centers_list)):
            for j in range(i + 1, len(centers_list)):
                dist = np.linalg.norm(
                    np.array(centers_list[i]) - np.array(centers_list[j])
                )
                name_pair = (names_list[i], names_list[j])
                intradistances.append({"pair": name_pair, "distance_m": dist})
                if dist < min_dist:
                    min_dist = dist
                    closest_pair = (centers_list[i], centers_list[j])
        if (
            closest_pair[0] is not None
            and closest_pair[1] is not None
            and reference_position is not None
            and pixel_per_meters > 0
        ):
            pt1 = np.array(
                [
                    int(reference_position[0] + closest_pair[0][0] * pixel_per_meters),
                    int(reference_position[1] + closest_pair[0][1] * pixel_per_meters),
                ]
            )
            pt2 = np.array(
                [
                    int(reference_position[0] + closest_pair[1][0] * pixel_per_meters),
                    int(reference_position[1] + closest_pair[1][1] * pixel_per_meters),
                ]
            )
            vec = pt2 - pt1
            dist_px = np.linalg.norm(vec)
            if dist_px != 0:
                direction = vec / dist_px
                radius = 100
                start = pt1 + direction * radius
                end = pt2 - direction * radius
            else:
                start = pt1
                end = pt2
            cv2.line(
                frame,
                tuple(start.astype(int)),
                tuple(end.astype(int)),
                (255, 255, 255),
                2,
            )
            dist_text = f"{min_dist * 1000:.0f}mm"
            midpoint = ((pt1[0] + pt2[0]) // 2, (pt1[1] + pt2[1]) // 2)
            cv2.putText(
                frame,
                dist_text,
                (midpoint[0] - 20, midpoint[1] + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1,
            )
    return intradistances
