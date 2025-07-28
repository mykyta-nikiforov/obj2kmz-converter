# OBJ to KMZ Converter

Convert 3D models from OBJ format to KMZ for use in ATAK.


## Features
- OBJ to DAE format convertion (using [Assimp](https://github.com/assimp/assimp) library) and packaging to KMZ format
- Automatic ground detection and alignment using RANSAC plane fitting (using [pyRANSAC-3D](https://github.com/leomariga/pyRANSAC-3D))
- Georeferencing support with UTM coordinates (using [pyproj](https://pyproj4.github.io/pyproj/stable/))
- ATAK compatibility

## Installation
### From source
```bash
git clone https://github.com/mykyta-nikiforov/obj2kmz-converter.git
cd obj2kmz-converter

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Or use pipx for global installation
pipx install -e . && pipx ensurepath
```

### System dependencies
You'll need Assimp installed:

**Ubuntu/Debian:**
```bash
sudo apt-get install libassimp-dev assimp-utils python3-pip python3-venv

# Optional, for global installation
sudo apt-get install pipx
```

**MacOS:**
```bash
brew install python assimp
# Optional, for global installation
brew install pipx
```

## Usage

Basic conversion:
```bash
obj2kmz OBJ_FILE GEO_FILE OUTPUT_PATH
```

**Arguments:**
- `OBJ_FILE` - Path to the 3D model file (.obj format)
- `GEO_FILE` - Path to the georeferencing file (.txt with UTM coordinates)
- `OUTPUT_PATH` - Path where the converted KMZ file will be saved

### Example
```bash
obj2kmz e211ba81-0deb-4f26-abb6-faa10f174d93/texturing/textured_model_geo.obj \
        e211ba81-0deb-4f26-abb6-faa10f174d93/georeferencing/georeferencing_model_geo.txt \
        output/model.kmz
```

Your georeferencing file should contain UTM coordinates:
```
WGS84 UTM 35N
418574 5345544
```

### Options

- `--no-textures` - Skip texture files for smaller output
- `--heading DEGREES` - Model rotation around Z-axis (default: 180)
- `--tilt DEGREES` - Model rotation around X-axis (default: -90)
- `--roll DEGREES` - Model rotation around Y-axis (default: 0)
- `--verbose` - Enable detailed logging

### Examples

```bash
# Lightweight version
obj2kmz model.obj georef.txt output.kmz --no-textures

# Custom orientation
obj2kmz model.obj georef.txt output.kmz --heading 90 --tilt -45
```

## Docker

```bash
docker build -t obj2kmz .

docker run --rm \
  -v $(pwd)/e211ba81-0deb-4f26-abb6-faa10f174d93:/app/input \
  -v $(pwd)/output:/app/output \
  obj2kmz \
  /app/input/texturing/textured_model_geo.obj \
  /app/input/georeferencing/georeferencing_model_geo.txt \
  /app/output/model_normal.kmz
```

## Input Files

- `.obj` file - Your 3D model
- `.mtl` file - Material definitions (same directory as OBJ)
- Texture files - PNG/JPG images referenced by MTL
- `georeferencing_model_geo.txt` - UTM coordinates