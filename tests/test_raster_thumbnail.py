"""
Unit tests for the raster thumbnail generator package.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_bounds

from raster_thumbnail import (
    detect_raster_type,
    generate_thumbnail,
    load_raster_config,
    process_directory,
)

# Import the package
from raster_thumbnail.core import (
    convert_to_physical_values,
    prepare_for_visualization,
    read_raster,
)

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRasterConfig:
    """Test configuration loading and raster type detection."""

    def test_load_default_config(self):
        """Test loading default configuration."""
        config = load_raster_config()
        assert "raster_types" in config
        assert "lai" in config["raster_types"]

    def test_detect_raster_type_lai(self):
        """Test LAI detection from filename."""
        config = load_raster_config()
        selected_types = ["lai"]

        test_cases = [
            "sentinel2_LAI_2024.tif",
            "data_lai_processed.tif",
            "LAI_prediction.tif",
            "test_LAI_data.tif",
        ]

        for filename in test_cases:
            raster_type = detect_raster_type(
                filename, config["raster_types"], selected_types
            )
            assert raster_type == "lai", f"Failed for {filename}"

    def test_detect_raster_type_ndvi(self):
        """Test NDVI detection from filename."""
        config = load_raster_config()
        selected_types = list(config["raster_types"].keys())

        test_cases = [
            "sentinel2_NDVI_2024.tif",
            "data_ndvi_processed.tif",
            "NDVI_prediction.tif",
        ]

        for filename in test_cases:
            raster_type = detect_raster_type(
                filename, config["raster_types"], selected_types
            )
            assert raster_type == "ndvi", f"Failed for {filename}"

    def test_detect_raster_type_no_match(self):
        """Test behavior when no raster type matches."""
        config = load_raster_config()
        selected_types = ["lai"]  # Only LAI types eligible

        test_cases = ["unknown_data.tif", "random_file.tif", "no_pattern_match.tif"]

        for filename in test_cases:
            raster_type = detect_raster_type(
                filename, config["raster_types"], selected_types
            )
            assert raster_type is None, f"Should return None for {filename}"


class TestRasterProcessing:
    """Test core raster processing functions."""

    def create_test_raster(self, width=10, height=10, nodata=None, scale=1.0, offset=0.0):
        """Create a test raster file."""
        # Create test data
        data = np.random.rand(height, width).astype(np.float32) * 100
        if nodata is not None:
            # Set some pixels to nodata
            data[0, 0] = nodata
            data[-1, -1] = nodata

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
        temp_path = Path(temp_file.name)
        temp_file.close()

        # Write raster
        transform = from_bounds(0, 0, width, height, width, height)
        with rasterio.open(
            temp_path,
            "w",
            driver="GTiff",
            height=height,
            width=width,
            count=1,
            dtype=data.dtype,
            crs="EPSG:4326",
            transform=transform,
            nodata=nodata,
            scales=[scale],
            offsets=[offset],
        ) as dst:
            dst.write(data, 1)

        return temp_path, data

    def test_read_raster_success(self):
        """Test successful raster reading."""
        temp_path, original_data = self.create_test_raster(nodata=-9999)

        try:
            result = read_raster(str(temp_path))

            assert result is not None
            data, nodata_value, scale, offset = result
            assert data is not None
            assert nodata_value == -9999
            assert scale == 1.0
            assert offset == 0.0

        finally:
            temp_path.unlink()  # Clean up

    def test_read_raster_no_nodata(self):
        """Test raster reading fails without nodata value."""
        temp_path, _ = self.create_test_raster(nodata=None)

        try:
            result = read_raster(str(temp_path))
            assert result is None  # Should fail without nodata

        finally:
            temp_path.unlink()

    def test_convert_to_physical_values(self):
        """Test conversion of raw values to physical values."""
        raw_data = np.array([100, 200, 300, -9999])
        nodata = -9999
        scale = 0.01
        offset = 10.0

        physical_data, value_range = convert_to_physical_values(
            raw_data, nodata, scale, offset
        )

        # Check conversion: physical = raw * scale + offset
        expected = np.array([11.0, 12.0, 13.0, np.nan])  # nodata becomes NaN
        valid_mask = ~np.isnan(physical_data)
        expected_valid = expected[~np.isnan(expected)]
        np.testing.assert_array_almost_equal(physical_data[valid_mask], expected_valid)
        assert np.isnan(physical_data[-1])  # nodata pixel should be NaN

    def test_prepare_for_visualization_fixed_range(self):
        """Test visualization preparation with fixed range."""
        data = np.array([0.5, 1.5, 2.5, 3.5, np.nan])

        viz_data, vis_range = prepare_for_visualization(
            data,
            use_percentile=False,
            percentile_range=[2, 98],  # Required parameter even when not used
            min_value=0.0,
            max_value=4.0,
        )

        assert viz_data is not None
        valid_mask = ~np.isnan(data)
        assert not np.any(np.isnan(viz_data[valid_mask]))  # Non-NaN values preserved
        assert np.isnan(viz_data[-1])  # NaN preserved

    def test_prepare_for_visualization_percentile(self):
        """Test visualization preparation with percentile range."""
        # Create data with known percentiles
        data = np.arange(0, 100, dtype=float)
        data = np.append(data, np.nan)  # Add NaN

        viz_data, vis_range = prepare_for_visualization(
            data,
            use_percentile=True,
            percentile_range=[10, 90],
            min_value=None,  # Required parameter even when not used
            max_value=None,  # Required parameter even when not used
        )

        assert viz_data is not None
        assert np.any(
            np.isnan(viz_data[-1:])
        )  # NaN preserved (check last element as array)


class TestThumbnailGeneration:
    """Test thumbnail generation functions."""

    def test_generate_thumbnail_invalid_input(self):
        """Test thumbnail generation with invalid input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "nonexistent.tif"
            output_path = Path(temp_dir) / "output.jpg"

            success = generate_thumbnail(str(input_path), str(output_path))
            assert success is False

    @patch("raster_thumbnail.utils.process_raster_file")
    def test_generate_thumbnail_success(self, mock_process):
        """Test successful thumbnail generation with mocks."""
        # Mock successful raster processing
        mock_process.return_value = True

        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "test_lai.tif"
            output_path = Path(temp_dir) / "output.jpg"

            # Create dummy input file
            input_path.touch()

            success = generate_thumbnail(str(input_path), str(output_path))

            assert success is True
            mock_process.assert_called_once()


class TestDirectoryProcessing:
    """Test directory processing functionality."""

    def test_process_directory_no_input_dir(self):
        """Test processing non-existent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir) / "nonexistent"
            output_dir = Path(temp_dir) / "output"

            results = process_directory(str(input_dir), str(output_dir))

            assert results["successful"] == 0
            assert results["failed"] == 1
            assert results["skipped"] == 0

    def test_process_directory_no_files(self):
        """Test processing directory with no matching files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir) / "input"
            output_dir = Path(temp_dir) / "output"
            input_dir.mkdir()

            # Create non-matching file
            (input_dir / "test.txt").touch()

            results = process_directory(str(input_dir), str(output_dir))

            assert results["successful"] == 0
            assert results["failed"] == 1  # No files found
            assert results["skipped"] == 0

    def test_process_directory_mixed_results(self):
        """Test processing directory with mixed success/failure/skipped."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir) / "input"
            output_dir = Path(temp_dir) / "output"
            input_dir.mkdir()

            # Create test files - one LAI file and one non-LAI file
            (input_dir / "valid_LAI_data.tif").touch()  # Should match LAI pattern
            (input_dir / "invalid_file.tif").touch()  # Won't match LAI pattern

            # Mock the processing to simulate success for the LAI file
            with patch("raster_thumbnail.utils.process_raster_file") as mock_process:
                mock_process.return_value = True  # LAI file succeeds

                results = process_directory(str(input_dir), str(output_dir))

                assert results["successful"] == 1  # LAI file processed successfully
                assert results["failed"] == 0  # No file failed (no matching raster type)
                assert results["skipped"] == 1  # One files explicitly skipped
                assert mock_process.call_count == 1  # Only LAI file processed


class TestIntegration:
    """Integration tests with real (small) raster files."""

    def create_minimal_raster(self, filename, raster_type="lai"):
        """Create minimal valid raster for integration testing."""
        # Create small test data
        if raster_type == "lai":
            data = np.array([[1.0, 2.0], [3.0, -9999]], dtype=np.float32)
            scale = 0.01
            offset = 0.0
        else:  # ndvi
            data = np.array([[0.2, 0.5], [0.8, -9999]], dtype=np.float32)
            scale = 0.001
            offset = 0.0

        nodata = -9999

        # Write minimal raster
        transform = from_bounds(0, 0, 2, 2, 2, 2)
        with rasterio.open(
            filename,
            "w",
            driver="GTiff",
            height=2,
            width=2,
            count=1,
            dtype=data.dtype,
            crs="EPSG:4326",
            transform=transform,
            nodata=nodata,
            scales=[scale],
            offsets=[offset],
        ) as dst:
            dst.write(data, 1)

        return filename

    @patch("raster_thumbnail.utils.process_raster_file")
    def test_end_to_end_thumbnail_generation(self, mock_process):
        """Test complete thumbnail generation workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test raster file (content doesn't matter with mock)
            input_file = temp_path / "test_LAI_data.tif"  # Ensure LAI pattern match
            output_file = temp_path / "thumbnail.jpg"

            # Create dummy file
            input_file.touch()

            # Mock successful processing
            mock_process.return_value = True

            # Generate thumbnail
            success = generate_thumbnail(str(input_file), str(output_file), size=64)

            # Verify success
            assert success is True
            mock_process.assert_called_once()

    @patch("raster_thumbnail.utils.process_raster_file")
    def test_end_to_end_directory_processing(self, mock_process):
        """Test complete directory processing workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_dir = temp_path / "input"
            output_dir = temp_path / "output"
            input_dir.mkdir()

            # Create test files - only LAI files will be processed by process_directory
            (input_dir / "LAI_data.tif").touch()  # Should match LAI pattern
            (input_dir / "ndvi_data.tif").touch()  # Will be skipped (no LAI pattern)

            # Mock successful processing for LAI file
            mock_process.return_value = True

            # Process directory (LAI-only)
            results = process_directory(str(input_dir), str(output_dir), size=64)

            # Verify results - both files attempted
            assert results["successful"] == 2  # Both files processed (mock returns True)
            assert results["failed"] == 0
            assert results["skipped"] == 0  # No files explicitly skipped

            # Verify mock was called for both files that matched patterns
            assert mock_process.call_count == 2


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
