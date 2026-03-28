# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-09-28

### Added
- Initial release of raster-thumbnail library
- Automatic raster type detection for LAI, NDVI, CCC, CDMC, PSRI, and soil moisture
- High-level convenience functions: `generate_thumbnail()` and `process_directory()`
- Core functions for advanced users
- Professional logging with separate files by severity level
- Metadata-driven processing using scale, offset, and nodata values from raster files
- Scientific visualization with optimized colormaps for each raster type:
  - LAI: `Greens` colormap for vegetation density
  - NDVI: `RdYlGn` colormap for vegetation health
  - CCC: `plasma` colormap for chlorophyll concentration
  - CDMC: `YlOrBr` colormap for dry matter content
  - PSRI: `autumn` colormap for senescence indication
  - Soil Moisture: `Blues` colormap for water content
- Comprehensive documentation and examples

### Features
- Support for multiple raster types with automatic detection
- Clean library API for easy integration
- Configurable visualization parameters
- Error handling and logging
- Type hints for better development experience
