# Raster Thumbnail Generator

A Python library for generating thumbnail images from various types of raster files with automatic type detection and appropriate scientific visualization.

## Features

- **Automatic raster type detection** based on filename patterns
- **Multiple raster types supported**: LAI, NDVI, CCC, CDMC, PSRI, soil moisture
- **Scientific visualization** with proper scaling, colormaps, and units
- **Metadata-driven processing** using scale, offset, and nodata values from raster files
- **High-quality thumbnails** with colorbars using matplotlib
- **Configurable logging**: Use Python's standard logging (no forced files/locations)
- **Configurable**: JSON-based configuration for adding new raster types
- **Easy-to-use API** for both single files and batch processing
- **No fallback values**: Requires proper raster metadata (no hardcoded assumptions)

## Installation

### Latest stable version:
```bash
pip install git+https://github.com/GNSSP-AgroHub/raster-thumbnail.git@main
```

### Latest development version:
```bash
pip install git+https://github.com/GNSSP-AgroHub/raster-thumbnail.git@implementation
```

### In requirements.txt:
```txt
# Latest stable
git+https://github.com/GNSSP-AgroHub/raster-thumbnail.git@main

# Latest development
git+https://github.com/GNSSP-AgroHub/raster-thumbnail.git@implementation

# Specific version (when available)
git+https://github.com/GNSSP-AgroHub/raster-thumbnail.git@v0.1.0
```

### For development:
```bash
git clone https://github.com/GNSSP-AgroHub/raster-thumbnail.git
cd raster-thumbnail
pip install -e .
```

## Quick Start

### Generate a single thumbnail

```python
from raster_thumbnail import generate_thumbnail

# Generate thumbnail from a LAI raster file
success = generate_thumbnail('lai_data.tif', 'thumbnail.jpg')
if success:
    print("Thumbnail generated successfully!")
```

### Process an entire directory

```python
from raster_thumbnail import process_directory

# Process all TIFF files in a directory
results = process_directory('data/', 'thumbnails/')
print(f"Successfully processed {results['successful']} files")
```

### Advanced usage with custom parameters

```python
from raster_thumbnail import generate_thumbnail

# Generate thumbnail with custom size and colormap
success = generate_thumbnail(
    input_path='ndvi_data.tif',
    output_path='ndvi_thumbnail.jpg',
    size=512,
    colormap='RdYlGn'
)
```

## API Reference

### `generate_thumbnail(input_path, output_path, size=256, colormap=None, config_path="raster_config.json")`

Generate a thumbnail from a single raster file.

**Parameters:**
- `input_path` (str|Path): Path to the input raster file
- `output_path` (str|Path): Path where the thumbnail will be saved
- `size` (int): Thumbnail size in pixels (default: 256)
- `colormap` (str): Colormap to use (default: auto-detect from config)
- `config_path` (str): Path to the configuration file

**Returns:**
- `bool`: True if successful, False otherwise

### `process_directory(input_dir, output_dir, file_pattern="*.tif", size=256, colormap=None, config_path="raster_config.json")`

Process all raster files in a directory and generate thumbnails.

**Parameters:**
- `input_dir` (str|Path): Directory containing raster files
- `output_dir` (str|Path): Directory where thumbnails will be saved
- `file_pattern` (str): File pattern to match (default: "*.tif")
- `size` (int): Thumbnail size in pixels (default: 256)
- `colormap` (str): Colormap to use (default: auto-detect from config)
- `config_path` (str): Path to the configuration file

**Returns:**
- `dict`: Summary with counts of successful, failed, and skipped files

## Supported Raster Types

The library automatically detects raster types based on filename patterns:

- **LAI (Leaf Area Index)**: `*LAI*`, `*lai*`, `*leaf_area*` patterns → **Greens** colormap
- **NDVI (Normalized Difference Vegetation Index)**: `*NDVI*`, `*ndvi*` patterns → **RdYlGn** colormap
- **CCC (Canopy Chlorophyll Content)**: `*Ccc*`, `*CCC*`, `*ccc*`, `*chlorophyll*` patterns → **plasma** colormap
- **CDMC (Canopy Dry Matter Content)**: `*Cdmc*`, `*CDMC*`, `*cdmc*`, `*dry_matter*` patterns → **YlOrBr** colormap
- **PSRI (Plant Senescence Reflectance Index)**: `*PSRI*`, `*psri*`, `*senescence*` patterns → **autumn** colormap
- **Soil Moisture**: `*soil_moisture*`, `*SM*`, `*moisture*` patterns → **Blues** colormap

Each type has its own:
- Scientific value ranges (e.g., NDVI: -1 to 1, LAI: 0 to 6)
- Optimized colormaps for the data type
- Physical units (e.g., μg/cm² for CCC, m³/m³ for soil moisture)
- Visualization parameters

### Type Detection Behavior

The library uses an `selected_types` approach for type detection:

- **`generate_thumbnail()`**: Considers all available raster types from the configuration
- **`process_directory()`**: Currently restricted to LAI files only
- **No fallback**: Files that don't match any eligible type patterns are skipped, not processed with generic settings

This ensures strict type checking and prevents incorrect processing of unrecognized raster types.

## Available Colormaps

Colormaps used for different raster types:
- **`Greens`** - LAI (Leaf Area Index) - Green intensity for vegetation density
- **`RdYlGn`** - NDVI - Red-Yellow-Green for vegetation health
- **`plasma`** - CCC (Chlorophyll Content) - Purple-to-yellow for concentration
- **`YlOrBr`** - CDMC (Dry Matter) - Brown tones for dry matter content
- **`autumn`** - PSRI - Red-yellow for senescence indication
- **`Blues`** - Soil Moisture - Blue intensity for water content

Other available matplotlib colormaps:
- `viridis`, `cividis` - Perceptually uniform, colorblind-friendly
- `turbo` - High contrast for scientific data
- `coolwarm` - Blue-white-red for diverging data

## Logging Configuration

The library uses Python's standard logging and doesn't force any file locations or handlers. You configure logging as needed:

### Basic logging setup (optional):

```python
import logging
from raster_thumbnail import generate_thumbnail
from raster_thumbnail.logging_config import setup_basic_logging

# Optional: Setup basic console logging
logger = setup_basic_logging(level=logging.INFO)

# Your code
success = generate_thumbnail('data.tif', 'thumb.jpg')
```

### Custom logging (recommended):

```python
import logging
from raster_thumbnail import generate_thumbnail

# Configure logging however you want
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('my_app.log'),  # Your log file
        logging.StreamHandler()             # Console output
    ]
)

# Your code
success = generate_thumbnail('data.tif', 'thumb.jpg')
```

### Advanced file logging (optional helper):

```python
from raster_thumbnail.logging_config import setup_file_logging

# Setup logging to specific file with console output
logger = setup_file_logging('thumbnails.log', level=logging.DEBUG, console=True)
```

## Configuration

The library uses a JSON configuration file (`raster_config.json`) to define raster types and their properties. You can customize this file to add new raster types or modify existing ones.

Example configuration structure:

```json
{
  "raster_types": {
    "lai": {
      "name": "Leaf Area Index",
      "unit": "LAI (m²/m²)",
      "colormap": "RdYlGn",
      "metadata_detection": {
        "filename_patterns": ["*lai*", "*LAI*"]
      },
      "visualization": {
        "use_percentile": false,
        "min_value": 0,
        "max_value": 6
      }
    }
  }
}
```

## Requirements

- Python >= 3.8
- numpy >= 1.20.0
- rasterio >= 1.2.0
- matplotlib >= 3.3.0
- Pillow >= 8.0.0

## How it Works

1. **Raster Type Detection**: Automatically detects raster type based on filename patterns
2. **Metadata Reading**: Uses `rasterio` to read scale, offset, and nodata values from raster metadata
3. **Physical Value Conversion**: Converts raw pixel values to actual physical values using metadata
4. **Intelligent Visualization**: Applies appropriate colormaps and value ranges based on raster type
5. **Thumbnail Generation**: Creates high-quality thumbnails with colorbars using `matplotlib`

## Metadata Requirements

The library requires proper raster metadata and will not use fallback values:
- **Scale factor**: Must be present in raster metadata
- **Offset**: Must be present in raster metadata
- **Nodata value**: Must be defined in raster metadata

This ensures accurate physical value conversion and prevents incorrect assumptions.

## Adding New Raster Types

To add a new raster type, edit `raster_config.json`:

1. Add the new type to `raster_types`
2. Define filename patterns for detection
3. Set appropriate colormap and visualization parameters

Note: The library now uses `selected_types` lists to control which raster types are considered during processing, rather than a global priority list. This allows for more flexible type filtering per use case.

## Examples

### Basic Usage

```python
import raster_thumbnail as rt

# Single file
rt.generate_thumbnail('sentinel2_lai.tif', 'lai_thumb.jpg')

# Directory processing
results = rt.process_directory('satellite_data/', 'thumbnails/')
print(f"Generated {results['successful']} thumbnails")
```

### Custom Configuration

```python
from raster_thumbnail import generate_thumbnail

# Use custom configuration file
success = generate_thumbnail(
    'custom_raster.tif',
    'thumbnail.jpg',
    config_path='my_config.json'
)
```

### Integration in Data Processing Pipeline

```python
from pathlib import Path
from raster_thumbnail import generate_thumbnail

def process_satellite_data(data_dir):
    data_path = Path(data_dir)
    thumbnail_dir = data_path / 'thumbnails'
    thumbnail_dir.mkdir(exist_ok=True)

    for raster_file in data_path.glob('*.tif'):
        thumbnail_path = thumbnail_dir / f"{raster_file.stem}_thumb.jpg"
        success = generate_thumbnail(raster_file, thumbnail_path)

        if success:
            print(f"Generated thumbnail for {raster_file.name}")
        else:
            print(f"Failed to process {raster_file.name}")
```

## Troubleshooting

### Common Issues:

1. **"No nodata value found"** - Ensure your raster files have proper nodata values in metadata
2. **"No valid data found"** - Check if your raster contains any non-nodata pixels
3. **Import errors** - Ensure all dependencies are installed: `pip install -r requirements.txt`
4. **Permission errors** - Check write permissions for output directory

### Debug Logging:

```python
import logging
from raster_thumbnail.logging_config import setup_basic_logging

# Enable debug logging
logger = setup_basic_logging(level=logging.DEBUG)
```

## License

Proprietary License - All rights reserved.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing guidelines, and contribution workflow.
