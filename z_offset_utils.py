#!/usr/bin/env python3
"""
Utilities for analyzing and manipulating Z-coordinates in 3D models.
"""

import logging
import numpy as np
from typing import List
from errors import FileProcessingError

logger = logging.getLogger(__name__)

VERTEX_PREFIX = 'v '
GROUND_LEVEL_PERCENTILE = 30


def _extract_z_coordinate_from_vertex_line(line: str) -> float:
    if not line.startswith(VERTEX_PREFIX):
        raise ValueError("Not a vertex line")

    parts = line.split()
    if len(parts) < 4:
        raise ValueError("Invalid vertex format")

    return float(parts[3])


def _extract_all_z_coordinates_from_obj(obj_path: str) -> List[float]:
    z_values = []

    try:
        with open(obj_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith(VERTEX_PREFIX):
                    z_value = _extract_z_coordinate_from_vertex_line(line)
                    z_values.append(z_value)

    except Exception as e:
        raise RuntimeError(f"Failed to read OBJ file: {e}")

    if not z_values:
        raise ValueError("No valid vertices found in OBJ file")

    return z_values


def calculate_z_offset(obj_path: str) -> float:
    """
    Calculate optimal Z offset for dominant ground plane alignment.
    
    Uses the GROUND_LEVEL_PERCENTILE of Z coordinates to identify the dominant ground plane.
    This percentile approach filters out outlier vertices (like underground
    features or floating debris) while preserving the main ground plane,
    ensuring the model aligns properly with the dominant ground plane.
    
    Args:
        obj_path: Path to the OBJ file
        
    Returns:
        float: Optimal Z offset for ground plane alignment
    """
    logger.info("Analyzing model geometry for dominant ground plane detection...")

    z_values = _extract_all_z_coordinates_from_obj(obj_path)
    z_array = np.array(z_values)

    optimal_offset = float(np.percentile(z_array, GROUND_LEVEL_PERCENTILE))

    logger.info(
        f"Ground plane analysis complete: {len(z_array):,} vertices, Z-range: {float(z_array.min()):.3f} to {float(z_array.max()):.3f}, ground plane offset: {optimal_offset:.3f}, model height: {float(z_array.max()) - optimal_offset:.3f} units")

    return optimal_offset


def _apply_z_offset_to_vertex_line(parts: List[str], z_offset: float) -> str:
    if len(parts) < 4:
        raise ValueError("Invalid vertex format")

    x = float(parts[1])
    y = float(parts[2])
    z = float(parts[3])
    z_fixed = z - z_offset
    return f"{VERTEX_PREFIX}{x} {y} {z_fixed}\n"


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
