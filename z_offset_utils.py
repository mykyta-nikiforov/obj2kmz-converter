#!/usr/bin/env python3
"""
Utilities for analyzing and manipulating Z-coordinates in 3D models.
"""

import logging
from typing import List

import numpy as np
import pyransac3d as pyrsc

from errors import FileProcessingError

logger = logging.getLogger(__name__)

VERTEX_PREFIX = 'v '


def calculate_z_offset(obj_path: str, threshold: float = 0.1, max_iterations: int = 1000) -> float:
    """
    Calculate optimal Z offset using RANSAC plane fitting.

    Args:
        obj_path: Path to the OBJ file
        threshold: Distance threshold for inlier points (default: 0.1)
        max_iterations: Maximum RANSAC iterations (default: 1000)

    Returns:
        float: optimal_offset
    """
    logger.info("Analyzing model geometry using RANSAC plane fitting...")

    vertices = _extract_all_vertices_from_obj(obj_path)
    optimal_offset = _calculate_offset(vertices, threshold, max_iterations)

    logger.info(f"RANSAC plane fitting complete. Ground plane offset: {optimal_offset:.3f}")
    return optimal_offset


def apply_z_offset_to_obj(input_obj: str, output_obj: str, z_offset: float) -> None:
    """
    Apply Z-offset to OBJ file by subtracting the offset from all vertices.

    Args:
        input_obj: Path to input OBJ file
        output_obj: Path to output OBJ file
        z_offset: Z offset to subtract from all vertices
    """
    logger.info(f"Subtracting Z offset: {z_offset} and creating grounded OBJ: {output_obj}")

    try:
        with open(input_obj, 'r') as f_in, \
                open(output_obj, 'w') as f_out:

            for line_num, line in enumerate(f_in, 1):
                processed_line = _process_obj_line_with_z_offset(line, z_offset)
                f_out.write(processed_line)

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise FileProcessingError(f"Failed to process OBJ file: {e}") from e

    logger.info(f"Successfully processed OBJ file with Z offset: {z_offset}, output: {output_obj}")


def _extract_all_vertices_from_obj(obj_path: str) -> np.ndarray:
    """
    Extract all vertex coordinates from OBJ file as numpy array.
    
    Args:
        obj_path: Path to the OBJ file
        
    Returns:
        np.ndarray: Array of shape (N, 3) containing vertex coordinates
    """
    vertices = []

    with open(obj_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith(VERTEX_PREFIX):
                parts = line.split()
                if len(parts) >= 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertices.append([x, y, z])

    if not vertices:
        raise ValueError("No valid vertices found in OBJ file")

    return np.array(vertices)


def _calculate_offset(vertices: np.ndarray, threshold: float, max_iterations: int) -> float:
    plane = pyrsc.Plane()
    plane_eq, inliers = plane.fit(vertices, threshold, maxIteration=max_iterations)

    # Calculate Z offset from plane equation
    A, B, C, D = plane_eq

    # Calculate the Z offset (distance from origin to plane along Z-axis)
    # For a horizontal plane (A=0, B=0, C=1), this would be -D
    # For general planes, find the Z-coordinate at (0,0,z) that satisfies the plane equation
    if abs(C) > 1e-6:  # Avoid division by zero
        optimal_offset = -D / C
    else:
        # If plane is vertical, use the mean Z of inlier points
        optimal_offset = float(np.mean(vertices[inliers, 2]))
        logger.warning("Plane is nearly vertical, using mean Z of inlier points")

    return optimal_offset


def _process_obj_line_with_z_offset(line: str, z_offset: float) -> str:
    original_line = line
    line = line.strip()

    if not line:
        return original_line

    if line.startswith(VERTEX_PREFIX):
        parts = line.split()
        return _apply_z_offset_to_vertex_line(parts, z_offset)
    else:
        return original_line


def _apply_z_offset_to_vertex_line(parts: List[str], z_offset: float) -> str:
    if len(parts) < 4:
        raise ValueError("Invalid vertex format")

    x = float(parts[1])
    y = float(parts[2])
    z = float(parts[3])
    z_fixed = z - z_offset
    return f"{VERTEX_PREFIX}{x} {y} {z_fixed}\n"
