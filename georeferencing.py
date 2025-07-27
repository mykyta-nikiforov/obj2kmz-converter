#!/usr/bin/env python3
import logging
from enum import Enum

import pyproj
from errors import GeoreferencingError

logger = logging.getLogger(__name__)

WGS84_PROJ_STRING = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
UTM_PROJ_STRING_TEMPLATE = "+proj=utm +ellps=WGS84 +datum=WGS84 +units=m +no_defs"


class Hemisphere(Enum):
    NORTH = ("N", "north")
    SOUTH = ("S", "south")

    def __init__(self, code: str, projection_value: str):
        self.code = code
        self.projection_value = projection_value

    @classmethod
    def from_code(cls, code: str) -> 'Hemisphere':
        """Get hemisphere enum from code string."""
        for hemisphere in cls:
            if hemisphere.code == code:
                return hemisphere
        raise ValueError(f"Invalid hemisphere code: {code}")


def read_georeferencing_file(georef_path: str) -> tuple[float, float, int, Hemisphere]:
    """
    Read georeferencing information from the specified file.
    
    Args:
        georef_path: Path to the georeferencing file
        
    Returns:
        tuple[float, float, int, Hemisphere]: (easting, northing, utm_zone, hemisphere)
    """
    try:
        with open(georef_path, 'r') as f:
            lines = f.readlines()

        coord_system = lines[0].strip()  # Parse the first line to get coordinate system info
        coords = lines[1].strip().split()  # Parse the second line to get coordinates
        easting = float(coords[0])
        northing = float(coords[1])

        # Extract UTM zone and hemisphere from coordinate system string. Example: "WGS84 UTM 35N"
        parts = coord_system.split()
        utm_zone = int(parts[-1][:-1])  # Remove 'N' or 'S' and convert to int
        hemisphere_str = parts[-1][-1]  # 'N' or 'S'
        hemisphere = Hemisphere.from_code(hemisphere_str)
        return easting, northing, utm_zone, hemisphere

    except Exception as e:
        logger.error(f"Error reading georeferencing file: {e}")
        raise GeoreferencingError(f"Failed to read georeferencing file: {e}") from e


def utm_to_wgs84(easting: float, northing: float, utm_zone: int, hemisphere: Hemisphere) -> tuple[float, float]:
    """
    Convert UTM coordinates to WGS84 latitude/longitude.
    
    Args:
        easting: UTM easting coordinate
        northing: UTM northing coordinate
        utm_zone: UTM zone number
        hemisphere: Hemisphere enum value (NORTH or SOUTH)
        
    Returns:
        tuple[float, float]: (longitude, latitude)
    """
    utm_proj_string = f"{UTM_PROJ_STRING_TEMPLATE} +zone={utm_zone} +{hemisphere.projection_value}"
    transformer = pyproj.Transformer.from_crs(utm_proj_string, WGS84_PROJ_STRING, always_xy=True)
    longitude, latitude = transformer.transform(easting, northing)
    return longitude, latitude
