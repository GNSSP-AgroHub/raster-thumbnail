"""
Core functionality for raster thumbnail generation.
"""

import fnmatch
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import rasterio

from .logging_config import get_logger

# Initialize logger once for the entire module
logger = get_logger()


def load_raster_config(config_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Load raster type configuration from JSON file."""
    if config_path is None:
        config_path = Path(__file__).parent / "raster_config.json"

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError as e:
        logger.error(f"Configuration file {config_path} not found: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file {config_path}: {e}")
        raise


def detect_raster_type(
    file_path: Union[str, Path], raster_types: Dict[str, Any], selected_types: List[str]
) -> Optional[str]:
    """
    Detect raster type and return the detected type name.

    This function can be easily copied to other codebases.

    Args:
        file_path: Path to the raster file
        raster_types: Dictionary of raster type configurations
        selected_types: List of raster types in priority order

    Returns:
        str: Name of the detected raster type
    """
    filename = Path(file_path).name.lower()

    # Try to match filename patterns
    for raster_type in selected_types:
        type_config = raster_types[raster_type]
        patterns = type_config.get("metadata_detection", {}).get("filename_patterns", [])

        for pattern in patterns:
            if fnmatch.fnmatch(filename, pattern.lower()):
                logger.debug(f"Matched pattern '{pattern}' for type '{raster_type}'")
                return raster_type

    # No match found - return None
    logger.warning(f"No matching raster type found for file: {file_path}")
    return None


def read_raster(
    file_path: Union[str, Path]
) -> Optional[Tuple[np.ndarray, Optional[float], Optional[float], Optional[float]]]:
    """Read raster file and return data array and basic metadata."""

    try:
        with rasterio.open(file_path) as src:
            # Read the first band
            data = src.read(1)
            profile = src.profile

            # Extract scale and offset from band tags/metadata
            scale = None
            offset = None

            # Try to get scale and offset from band 1 tags
            band_tags = src.tags(1)

            # Check various possible tag names
            scale_keys = ["SCALE", "Scale", "scale"]
            offset_keys = ["OFFSET", "Offset", "offset"]

            for key in scale_keys:
                if key in band_tags:
                    scale = float(band_tags[key])
                    break

            for key in offset_keys:
                if key in band_tags:
                    offset = float(band_tags[key])
                    break

            # Check for scale/offset in profile
            if scale is None and "scales" in profile and profile["scales"]:
                scale = profile["scales"][0]
            if offset is None and "offsets" in profile and profile["offsets"]:
                offset = profile["offsets"][0]

            # Check rasterio source properties (most common location)
            if scale is None and hasattr(src, "scales") and src.scales:
                scale = src.scales[0]
            if offset is None and hasattr(src, "offsets") and src.offsets:
                offset = src.offsets[0]

            # Check global tags as well
            global_tags = src.tags()
            if scale is None:
                for key in scale_keys:
                    if key in global_tags:
                        scale = float(global_tags[key])
                        break
            if offset is None:
                for key in offset_keys:
                    if key in global_tags:
                        offset = float(global_tags[key])
                        break

            # Print all available tags for debugging
            logger.debug(f"Band tags: {band_tags}")
            if global_tags:
                logger.debug(f"Global tags: {global_tags}")

            # Get nodata value from raster metadata
            nodata_value = src.nodata
            logger.info(f"Nodata value from metadata: {nodata_value}")

            # Require all critical metadata from raster file (no fallbacks)
            if nodata_value is None:
                raise ValueError(
                    f"No nodata value found in raster metadata for {file_path}"
                )

            if scale is None:
                raise ValueError(
                    f"No scale factor found in raster metadata for {file_path}"
                )

            if offset is None:
                raise ValueError(f"No offset found in raster metadata for {file_path}")

            logger.info(
                "Raster metadata - Scale: {}, Offset: {}, Nodata: {}".format(
                    scale, offset, nodata_value
                )
            )
            logger.debug(f"Raster size: {data.shape}, Data type: {data.dtype}")

            return data, nodata_value, scale, offset
    except Exception as e:
        logger.error(f"Error reading raster file {file_path}: {e}")
        return None


def convert_to_physical_values(
    data: np.ndarray, nodata_value: float, scale: float, offset: float
) -> Tuple[Optional[np.ndarray], Optional[Tuple[float, float]]]:
    """Convert scaled raster data to actual physical values using metadata."""
    # All required metadata parameters must be provided
    if nodata_value is None:
        raise ValueError("nodata_value is required and cannot be None")
    if scale is None:
        raise ValueError("scale is required and cannot be None")
    if offset is None:
        raise ValueError("offset is required and cannot be None")

    logger.debug(f"Using nodata value from metadata: {nodata_value}")
    logger.debug(f"Using metadata scale factor: {scale}")
    logger.debug(f"Using metadata offset: {offset}")

    valid_mask = data != nodata_value
    valid_data = data[valid_mask]

    if len(valid_data) == 0:
        logger.warning("No valid raster data found - all pixels are nodata")
        return None, None

    logger.debug(f"Raw data range: {np.min(valid_data)} to {np.max(valid_data)}")
    logger.debug(
        f"Valid pixels: {
            len(valid_data)}/{data.size} ({len(valid_data)/data.size*100:.1f}%)"
    )

    # Apply scale and offset from metadata
    physical_values = data.astype(np.float64) * scale + offset

    # Set nodata to NaN for proper handling
    physical_values[~valid_mask] = np.nan

    # Get actual physical value range for valid data
    valid_values = physical_values[valid_mask]
    value_min: float = float(np.min(valid_values))
    value_max: float = float(np.max(valid_values))
    logger.info(f"Actual physical range: {value_min:.3f} to {value_max:.3f}")

    return physical_values.astype(np.float32), (value_min, value_max)


def prepare_for_visualization(
    physical_values: np.ndarray,
    use_percentile: bool,
    percentile_range: Tuple[float, float],
    min_value: Optional[float],
    max_value: Optional[float],
) -> Tuple[np.ndarray, Tuple[float, float]]:
    """
    Prepare raster values for visualization
    using actual values with proper nodata handling.

    Args:
        physical_values: Actual physical values array
        use_percentile: Whether to use percentile-based range
        percentile_range: Tuple/list of (min_percentile, max_percentile)
        min_value: Configured minimum value (or None)
        max_value: Configured maximum value (or None)

    Returns:
        visualization_data: Physical values with NaN for nodata (proper transparency)
        display_range: Range for colorbar (value_min, value_max)
    """
    # Remove NaN values for processing
    valid_mask = ~np.isnan(physical_values)
    valid_values = physical_values[valid_mask]

    if len(valid_values) == 0:
        return np.full_like(physical_values, np.nan), (0, 1)

    value_min: float
    value_max: float

    if use_percentile:
        # Use percentile-based range for better contrast
        value_min = float(np.percentile(valid_values, percentile_range[0]))
        value_max = float(np.percentile(valid_values, percentile_range[1]))
        logger.info(f"Using percentile-based range: {value_min:.3f} to {value_max:.3f}")
    else:
        # Use scientific range or data range
        if min_value is not None and max_value is not None:
            value_min = min_value
            value_max = max(max_value, float(np.max(valid_values)))
            logger.info(f"Using configured range: {value_min} to {value_max:.3f}")
        else:
            value_min = float(np.min(valid_values))
            value_max = float(np.max(valid_values))
            logger.info(f"Using data range: {value_min:.3f} to {value_max:.3f}")

    # Keep actual physical values, set invalid areas to NaN for proper transparency
    visualization_data = np.copy(physical_values)
    visualization_data[~valid_mask] = np.nan

    logger.debug("Using actual physical values with NaN for nodata areas")
    return visualization_data, (value_min, value_max)


def create_thumbnail(
    data: np.ndarray,
    output_path: Path,
    nodata_value: float,
    scale: float,
    offset: float,
    use_percentile: bool,
    percentile_range: Tuple[float, float],
    min_value: Optional[float],
    max_value: Optional[float],
    raster_name: str,
    unit_label: str,
    colormap: str,
    thumbnail_size: int = 256,
) -> bool:
    """
    Create a thumbnail with colorbar using matplotlib.
    Returns True on success, False on failure.
    """
    # Convert to actual physical values
    physical_values, value_range = convert_to_physical_values(
        data, nodata_value, scale, offset
    )

    # Check if we have valid data
    if physical_values is None:
        raise ValueError("Cannot create thumbnail - no valid data found in raster")

    # Prepare values for visualization with proper nodata handling
    visualization_data, vis_range = prepare_for_visualization(
        physical_values, use_percentile, percentile_range, min_value, max_value
    )

    # Create figure
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(8, 4), gridspec_kw={"width_ratios": [4, 0.2]}
    )

    # Plot the data using actual physical values with proper nodata handling
    value_min, value_max = vis_range
    im = ax1.imshow(
        visualization_data, cmap=colormap, aspect="equal", vmin=value_min, vmax=value_max
    )

    ax1.set_title(f"{raster_name} Thumbnail", fontsize=10)
    ax1.axis("off")

    # Create colorbar with direct physical values (matplotlib handles ticks automatically)
    cbar = plt.colorbar(im, cax=ax2)
    cbar.set_label(unit_label, fontsize=8)

    # Tight layout
    fig.tight_layout()

    # Save with specific DPI to control size
    dpi = thumbnail_size / 4  # Approximate DPI for desired size
    fig.savefig(
        output_path, dpi=dpi, bbox_inches="tight", facecolor="white", edgecolor="none"
    )
    plt.close(fig)

    logger.info(f"Thumbnail created successfully: {output_path.name}")
    return True


def process_raster_file(
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    use_percentile: bool,
    percentile_range: Tuple[float, float],
    min_value: Optional[float],
    max_value: Optional[float],
    raster_name: str,
    unit_label: str,
    colormap: str,
    thumbnail_size: int = 256,
) -> bool:
    """Process a single raster file and generate thumbnail."""
    # Read raster data
    result = read_raster(input_path)
    if result is None:
        return False

    data, nodata_value, scale, offset = result

    # Ensure we have valid metadata values
    if nodata_value is None or scale is None or offset is None:
        logger.error(f"Missing required metadata for {input_path}")
        return False

    # Create output filename
    input_path_obj = Path(input_path)
    input_name = input_path_obj.stem
    output_filename = f"{input_name}_thumbnail.jpg"
    output_path = Path(output_dir) / output_filename

    try:
        create_thumbnail(
            data,
            output_path,
            nodata_value,
            scale,
            offset,
            use_percentile,
            percentile_range,
            min_value,
            max_value,
            raster_name,
            unit_label,
            colormap,
            thumbnail_size,
        )
        return True
    except Exception as e:
        logger.error(f"Error creating thumbnail for {input_path_obj.name}: {e}")
        return False
