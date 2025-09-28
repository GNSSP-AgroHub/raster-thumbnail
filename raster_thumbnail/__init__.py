"""
Raster Thumbnail Generator

A Python package for generating thumbnail images from various types of raster files
with automatic type detection and appropriate scientific visualization.

Usage:
    from raster_thumbnail import generate_thumbnail, process_directory

    # Generate single thumbnail
    generate_thumbnail('path/to/raster.tif', 'output/thumbnail.jpg')

    # Process entire directory
    process_directory('data/', 'thumbnails/')
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import (
    convert_to_physical_values,
    create_thumbnail,
    detect_raster_type,
    load_raster_config,
    prepare_for_visualization,
    process_raster_file,
    read_raster,
)
from .logging_config import (
    get_logger,
    setup_basic_logging,
    setup_file_logging,
    silence_third_party_loggers,
)
from .utils import generate_thumbnail, process_directory

__all__ = [
    # Core functions for advanced users
    "load_raster_config",
    "detect_raster_type",
    "read_raster",
    "convert_to_physical_values",
    "prepare_for_visualization",
    "create_thumbnail",
    "process_raster_file",
    # High-level convenience functions
    "generate_thumbnail",
    "process_directory",
    # Optional logging utilities
    "get_logger",
    "setup_basic_logging",
    "setup_file_logging",
    "silence_third_party_loggers",
]
