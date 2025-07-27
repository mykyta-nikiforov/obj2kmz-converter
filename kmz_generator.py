#!/usr/bin/env python3
import os
import zipfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def create_kml_content(dae_filename: str, longitude: float, latitude: float, 
                    heading: float, tilt: float, roll: float) -> str:
    template_path = Path(__file__).parent / "kml_template.xml"

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        kml_content = template_content.format(
            longitude=longitude,
            latitude=latitude,
            dae_filename=dae_filename,
            heading=heading,
            tilt=tilt,
            roll=roll
        )

        return kml_content

    except FileNotFoundError:
        raise FileNotFoundError(f"KML template not found: {template_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to process KML template: {e}")


def create_kmz(kml_content: str, dae_path: str, texture_files: list[str], output_kmz_path: str) -> str:
    try:
        with zipfile.ZipFile(output_kmz_path, 'w', zipfile.ZIP_DEFLATED) as kmz:
            kmz.writestr('doc.kml', kml_content)
            kmz.write(dae_path, os.path.basename(dae_path))
            for texture_file in texture_files:
                if os.path.exists(texture_file):
                    kmz.write(texture_file, os.path.basename(texture_file))

        logger.info(f"Successfully created KMZ file: {output_kmz_path}")
        return output_kmz_path

    except Exception as e:
        logger.error(f"Error creating KMZ file: {e}")
        raise
