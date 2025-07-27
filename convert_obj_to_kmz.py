#!/usr/bin/env python3
import sys
import argparse
import logging

from pipeline import Pipeline
from assimp_converter import AssimpModelConverter
from errors import ConverterScriptError


def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OBJ to KMZ converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-align to dominant ground plane
  python3 convert_obj_to_kmz.py model.obj georef.txt output.kmz
  
  # Lightweight version without textures
  python3 convert_obj_to_kmz.py model.obj georef.txt output.kmz --no-textures

  # Custom model orientation (rotate 90 degrees around Z-axis)
  python3 convert_obj_to_kmz.py model.obj georef.txt output.kmz --heading 90
  
  # Custom model orientation (no tilt, lay flat)
  python3 convert_obj_to_kmz.py model.obj georef.txt output.kmz --tilt 0
  
  # Full custom orientation
  python3 convert_obj_to_kmz.py model.obj georef.txt output.kmz --heading 45 --tilt -45 --roll 10
        """
    )

    parser.add_argument("obj_file", help="Path to input OBJ file")
    parser.add_argument("georef_file", help="Path to georeferencing file (UTM coordinates)")
    parser.add_argument("output_kmz", help="Path to output KMZ file")

    parser.add_argument("--no-textures", action="store_true",
                        help="Skip texture files for lightweight version")
    parser.add_argument("--heading", type=float, default=180.0, metavar="DEGREES",
                        help="Model rotation around Z-axis in degrees (default: 180)")
    parser.add_argument("--tilt", type=float, default=-90.0, metavar="DEGREES", 
                        help="Model rotation around X-axis in degrees (default: -90)")
    parser.add_argument("--roll", type=float, default=0.0, metavar="DEGREES",
                        help="Model rotation around Y-axis in degrees (default: 0)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging (DEBUG level)")

    args = parser.parse_args()

    setup_logging(verbose=args.verbose)

    try:
        model_converter = AssimpModelConverter()
        pipeline = Pipeline(model_converter)
        pipeline.convert_model(
            obj_file=args.obj_file,
            georef_file=args.georef_file,
            output_kmz=args.output_kmz,
            no_textures=args.no_textures,
            heading=args.heading,
            tilt=args.tilt,
            roll=args.roll
        )
    except ConverterScriptError as e:
        logging.error(f"Conversion failed: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
