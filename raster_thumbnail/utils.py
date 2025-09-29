"""
High-level convenience functions for raster thumbnail generation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .core import detect_raster_type, load_raster_config, process_raster_file
from .logging_config import get_logger


def generate_thumbnail(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    size: int = 256,
    colormap: Optional[str] = None,
    config_path: str = None,
    selected_types: Optional[list] = None,
) -> bool:
    """
    Generate a thumbnail from a single raster file.

    Args:
        input_path: Path to the input raster file
        output_path: Path where the thumbnail will be saved
        size: Thumbnail size in pixels (default: 256)
        colormap: Colormap to use (default: auto-detect from config)
        config_path: Path to the configuration file
        selected_types: List of raster types to consider (default: all types)

    Returns:
        bool: True if successful, False otherwise

    Example:
        >>> from raster_thumbnail import generate_thumbnail
        >>> success = generate_thumbnail('lai_data.tif', 'thumbnail.jpg')
    """
    # Setup logging
    logger = get_logger()

    # Convert to Path objects
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        logger.error(f"Input file does not exist: {input_path}")
        return False

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Load configuration
        raster_config = load_raster_config(config_path)
        selected_types = _get_selected_types(raster_config, selected_types)

        # Detect raster type
        detected_type = detect_raster_type(
            input_path, raster_config["raster_types"], selected_types
        )

        if detected_type is None:
            return False

        type_config = raster_config["raster_types"][detected_type]

        # Extract visualization parameters
        viz_config = type_config.get("visualization", {})
        use_percentile = viz_config.get("use_percentile", False)
        percentile_range = viz_config.get("percentile_range", [2, 98])
        min_value = viz_config.get("min_value")
        max_value = viz_config.get("max_value")

        # Extract display parameters
        raster_name = type_config.get("name", "Raster")
        unit_label = type_config.get("unit", "Value")
        default_colormap = type_config.get("colormap", "viridis")

        # Use provided colormap or default from config
        final_colormap = colormap if colormap is not None else default_colormap

        # Generate thumbnail
        success = process_raster_file(
            input_path,
            output_path.parent,
            use_percentile,
            percentile_range,
            min_value,
            max_value,
            raster_name,
            unit_label,
            final_colormap,
            size,
        )

        return success

    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
        return False


def process_directory(
    input_dir: Union[str, Path],
    output_dir: Union[str, Path],
    file_pattern: str = "*.tif",
    size: int = 256,
    colormap: Optional[str] = None,
    config_path: str = None,
    selected_types: Optional[list] = None,
) -> dict:
    """
    Process all raster files in a directory and generate thumbnails.

    Args:
        input_dir: Directory containing raster files
        output_dir: Directory where thumbnails will be saved
        file_pattern: File pattern to match (default: "*.tif")
        size: Thumbnail size in pixels (default: 256)
        colormap: Colormap to use (default: auto-detect from config)
        config_path: Path to the configuration file
        selected_types: List of raster types to consider (default: all types)

    Returns:
        dict: Summary with counts of successful, failed, and skipped files

    Example:
        >>> from raster_thumbnail import process_directory
        >>> results = process_directory('data/', 'thumbnails/')
        >>> print(f"Processed {results['successful']} files successfully")
    """
    # Get logger (user should configure logging as needed)
    logger = get_logger()

    # Convert to Path objects
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        return {"successful": 0, "failed": 1, "skipped": 0}

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Load configuration
        raster_config = load_raster_config(config_path)
        logger.info(f"Configuration loaded from {config_path}")
        selected_types = _get_selected_types(raster_config, selected_types)

        # Find raster files
        raster_files = list(input_dir.glob(file_pattern))

        if not raster_files:
            logger.error(
                "No raster files found in '{}' matching pattern '{}'".format(
                    input_dir, file_pattern
                )
            )
            return {"successful": 0, "failed": 1, "skipped": 0}

        logger.info(f"Found {len(raster_files)} raster file(s)")

        # Process each file
        success_count = 0
        failed_count = 0
        skipped_count = 0

        for raster_file in raster_files:
            # Detect raster type
            detected_type = detect_raster_type(
                raster_file, raster_config["raster_types"], selected_types
            )

            if detected_type is None:
                skipped_count += 1
                continue
            type_config = raster_config["raster_types"][detected_type]

            # Extract visualization parameters
            viz_config = type_config.get("visualization", {})
            use_percentile = viz_config.get("use_percentile", False)
            percentile_range = viz_config.get("percentile_range", [2, 98])
            min_value = viz_config.get("min_value")
            max_value = viz_config.get("max_value")

            # Extract display parameters
            raster_name = type_config.get("name", "Raster")
            unit_label = type_config.get("unit", "Value")
            default_colormap = type_config.get("colormap", "viridis")
            final_colormap = colormap if colormap is not None else default_colormap

            result = process_raster_file(
                raster_file,
                output_dir,
                use_percentile,
                percentile_range,
                min_value,
                max_value,
                raster_name,
                unit_label,
                final_colormap,
                size,
            )

            if result is True:
                success_count += 1
            elif result is False:
                failed_count += 1
            else:  # result is None for skipped files
                skipped_count += 1

        # Final summary
        logger.info("PROCESSING SUMMARY:")
        logger.info(f"Successful: {success_count}")
        if failed_count > 0:
            logger.info(f"Failed: {failed_count}")
        if skipped_count > 0:
            logger.info(f"Skipped (no valid data): {skipped_count}")
        logger.info(f"Thumbnails saved in: {output_dir}")

        return {
            "successful": success_count,
            "failed": failed_count,
            "skipped": skipped_count,
        }

    except Exception as e:
        logger.error(f"Error processing directory: {e}")
        return {"successful": 0, "failed": 1, "skipped": 0}


# private function to pick eligible raster types. if input is none, return all types
def _get_selected_types(
    raster_config: Dict[str, Any], selected_types: Optional[List[str]]
) -> List[str]:
    if selected_types is None:
        return list(raster_config["raster_types"].keys())
    else:
        return [t for t in selected_types if t in raster_config["raster_types"]]
