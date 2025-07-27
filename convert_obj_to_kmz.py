#!/usr/bin/env python3
import sys
import argparse
import logging

from converter import Converter
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
  
  # Manual Z-offset
  python3 convert_obj_to_kmz.py model.obj georef.txt output.kmz --z-offset 330.0
  
  # Lightweight version without textures
  python3 convert_obj_to_kmz.py model.obj georef.txt output.kmz --no-textures
        """
    )

    parser.add_argument("obj_file", help="Path to input OBJ file")
    parser.add_argument("georef_file", help="Path to georeferencing file (UTM coordinates)")
    parser.add_argument("output_kmz", help="Path to output KMZ file")

    parser.add_argument("--z-offset", type=float, metavar="OFFSET",
                        help="Manual Z offset to apply (subtracts from all Z coordinates). If not specified, automatic ground plane alignment is applied")
    parser.add_argument("--no-textures", action="store_true",
                        help="Skip texture files for lightweight version")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging (DEBUG level)")

    args = parser.parse_args()

    setup_logging(verbose=args.verbose)

    try:
        assimp_converter = AssimpModelConverter()
        converter = Converter(assimp_converter)
        converter.convert_model(
            obj_file=args.obj_file,
            georef_file=args.georef_file,
            output_kmz=args.output_kmz,
            z_offset=args.z_offset,
            no_textures=args.no_textures
        )
    except ConverterScriptError as e:
        logging.error(f"Conversion failed: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
