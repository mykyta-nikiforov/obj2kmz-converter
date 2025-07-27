#!/usr/bin/env python3
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DIFFUSE_MAP_KEY = 'map_Kd'


class ObjParser:

    @staticmethod
    def get_texture_files(obj_path: Path) -> set[str]:
        """
        Get all texture files referenced by an OBJ file.
        """
        obj_dir = obj_path.parent
        mtl_file = ObjParser._find_mtl_file(obj_path)

        if mtl_file:
            mtl_path = obj_dir / mtl_file
            return ObjParser._extract_texture_refs(mtl_path)

        return set()

    @staticmethod
    def _find_mtl_file(obj_path: Path) -> Optional[str]:
        """
        Find the material file reference in the OBJ file.
        """
        with open(obj_path, 'r') as f:
            for line in f:
                if line.startswith('mtllib '):
                    return line.split(' ', 1)[1].strip()
        return None

    @staticmethod
    def _extract_texture_refs(mtl_path: Path) -> set[str]:
        """
        Extract texture file references from the material file.
        """
        texture_refs = set()

        if mtl_path.exists():
            with open(mtl_path, 'r') as f:
                mtl_content = f.read()

            for line in mtl_content.split('\n'):
                if line.startswith(DIFFUSE_MAP_KEY):
                    texture_file = line.split(' ', 1)[1].strip()
                    texture_refs.add(texture_file)

        return texture_refs
