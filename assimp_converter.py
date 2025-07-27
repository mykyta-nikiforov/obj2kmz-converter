#!/usr/bin/env python3

import subprocess
import logging
from pathlib import Path
from obj_parser import ObjParser
from errors import ModelConversionError

logger = logging.getLogger(__name__)


class ModelConverter:

    def convert_obj_to_dae(self, obj_path: str, output_dir: str) -> str:
        raise NotImplementedError("Subclasses must implement convert_obj_to_dae")


class AssimpModelConverter(ModelConverter):
    def convert_obj_to_dae(self, obj_path: str, output_dir: str) -> str:
        """
        Convert an OBJ file to DAE format using assimp.

        Args:
            obj_path: Path to the OBJ file
            output_dir: Directory to save the DAE file

        Returns:
            str: Path to the created DAE file
        """
        obj_path = Path(obj_path)
        dae_path = Path(output_dir) / f"{obj_path.stem}.dae"

        try:
            cmd = [
                "assimp", "export",
                str(obj_path),
                str(dae_path),
                "-f", "collada",
                "--post-process", "Triangulate,GenerateNormals,OptimizeMeshes"
            ]

            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("Converted OBJ to DAE successfully")
            return str(dae_path)

        except subprocess.CalledProcessError as e:
            logger.error(f"Error converting OBJ to DAE: {e}\nstderr: {e.stderr}")
            raise ModelConversionError(f"Failed to convert OBJ to DAE: {e}") from e


def get_texture_paths(obj_path: str) -> list[str]:
    logger.info("Getting texture files...")
    obj_path = Path(obj_path)
    obj_dir = obj_path.parent
    texture_files = []

    try:
        texture_refs = ObjParser.get_texture_files(obj_path)

        for texture_ref in texture_refs:
            src_path = obj_dir / texture_ref
            if src_path.exists():
                texture_files.append(str(src_path))

        logger.info(f"Found {len(texture_files)} texture files")
        return texture_files

    except Exception as e:
        logger.warning(f"Could not get texture file paths: {e}")
        return []
