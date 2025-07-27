#!/usr/bin/env python3
import logging
import os
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)

from georeferencing import read_georeferencing_file, utm_to_wgs84
from kmz_generator import create_kml_content, create_kmz
from assimp_converter import get_texture_paths, ModelConverter
from z_offset_utils import calculate_z_offset, apply_z_offset_to_obj


class Pipeline:
    def __init__(self, converter: ModelConverter):
        self.converter = converter

    def convert_model(self, obj_file: str,
                      georef_file: str,
                      output_kmz: str,
                      z_offset: Optional[float] = None,
                      no_textures: bool = False,
                      heading: float = 180,
                      tilt: float = -90,
                      roll: float = 0) -> None:
        logger.info("Starting OBJ to KMZ conversion...")

        self._validate_inputs(obj_file, georef_file)
        self._ensure_output_directory(output_kmz)

        logger.info("Reading georeferencing information...")
        easting, northing, utm_zone, hemisphere = read_georeferencing_file(georef_file)
        longitude, latitude = utm_to_wgs84(easting, northing, utm_zone, hemisphere)
        logger.info(
            f"UTM: {easting}, {northing} (Zone {utm_zone}{hemisphere.code}) | WGS84: {longitude:.6f}, {latitude:.6f}")

        if z_offset is None:
            z_offset = calculate_z_offset(obj_file)

        with tempfile.TemporaryDirectory() as temp_dir:
            obj_file_to_convert = obj_file

            if z_offset != 0:
                obj_file_to_convert = self._apply_z_offset(obj_file, z_offset)

            logger.info("Converting OBJ to DAE format...")
            dae_path = self.converter.convert_obj_to_dae(obj_file_to_convert, temp_dir)
            dae_filename = os.path.basename(dae_path)

            texture_files = []
            if not no_textures:
                texture_files = get_texture_paths(obj_file)

            logger.info("Creating KMZ package...")
            kml_file_path = create_kml_content(dae_filename, longitude, latitude, heading, tilt, roll)
            create_kmz(kml_file_path, dae_path, texture_files, output_kmz)

        logger.info(f"Conversion completed successfully! Output: {output_kmz}")

    def _validate_inputs(self, obj_file: str, georef_file: str) -> None:
        if not os.path.exists(obj_file):
            raise FileNotFoundError(f"OBJ file not found: {obj_file}")
        if not os.path.exists(georef_file):
            raise FileNotFoundError(f"Georeferencing file not found: {georef_file}")

    def _ensure_output_directory(self, output_kmz: str) -> None:
        output_dir = os.path.dirname(output_kmz)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def _apply_z_offset(self, obj_file: str, z_offset: float) -> str:
        obj_dir = os.path.dirname(obj_file)
        obj_name = os.path.splitext(os.path.basename(obj_file))[0]
        offset_obj_path = os.path.join(obj_dir, f"{obj_name}_aligned.obj")

        logger.info(f"Applying ground plane alignment offset of {z_offset:.3f}...")
        apply_z_offset_to_obj(obj_file, offset_obj_path, z_offset)

        return offset_obj_path
