"""
Simple unit tests for the raster thumbnail generator package.
Tests core functionality without requiring pytest.
"""

import sys
import tempfile
from pathlib import Path

from raster_thumbnail import (
    detect_raster_type,
    generate_thumbnail,
    load_raster_config,
    process_directory,
)

# Import the package
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_load_config():
    """Test loading default configuration."""
    print("Testing config loading...")
    config = load_raster_config()
    assert "raster_types" in config
    assert "lai" in config["raster_types"]
    print("✅ Config loading test passed")


def test_raster_type_detection():
    """Test raster type detection from filenames."""
    print("Testing raster type detection...")
    config = load_raster_config()

    # Test LAI detection with LAI-only eligible types
    lai_files = ["sentinel2_LAI_2024.tif", "data_lai_processed.tif", "LAI_prediction.tif"]
    lai_eligible = ["lai"]
    for filename in lai_files:
        raster_type = detect_raster_type(filename, config["raster_types"], lai_eligible)
        assert raster_type == "lai", f"Failed LAI detection for {filename}"

    # Test NDVI detection with all eligible types
    ndvi_files = ["sentinel2_NDVI_2024.tif", "data_ndvi_processed.tif"]
    all_eligible = list(config["raster_types"].keys())
    for filename in ndvi_files:
        raster_type = detect_raster_type(filename, config["raster_types"], all_eligible)
        assert raster_type == "ndvi", f"Failed NDVI detection for {filename}"

    # Test no match behavior (should return None)
    unknown_files = ["unknown_data.tif", "random_file.tif"]
    for filename in unknown_files:
        raster_type = detect_raster_type(filename, config["raster_types"], lai_eligible)
        assert raster_type is None, f"Should return None for unknown file {filename}"

    print("✅ Raster type detection tests passed")


def test_generate_thumbnail_invalid_input():
    """Test thumbnail generation with invalid input."""
    print("Testing thumbnail generation with invalid input...")
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "nonexistent.tif"
        output_path = Path(temp_dir) / "output.jpg"

        success = generate_thumbnail(str(input_path), str(output_path))
        assert success is False

    print("✅ Invalid input test passed")


def test_process_directory_no_input():
    """Test processing non-existent directory."""
    print("Testing directory processing with invalid input...")
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "nonexistent"
        output_dir = Path(temp_dir) / "output"

        results = process_directory(str(input_dir), str(output_dir))

        assert results["successful"] == 0
        assert results["failed"] == 1
        assert results["skipped"] == 0

    print("✅ Directory processing test passed")


def test_process_directory_no_files():
    """Test processing directory with no matching files."""
    print("Testing directory processing with no files...")
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

    print("✅ No files test passed")


def test_process_directory_resilience():
    """Test that directory processing continues after failures."""
    print("Testing directory processing resilience...")
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        input_dir.mkdir()

        # Create test files (they won't be valid rasters, so will fail)
        (input_dir / "file1_lai.tif").touch()
        (input_dir / "file2_ndvi.tif").touch()
        (input_dir / "file3_elevation.tif").touch()

        results = process_directory(str(input_dir), str(output_dir))

        # All should fail (invalid rasters) but all should be attempted
        total_attempted = results["successful"] + results["failed"] + results["skipped"]
        assert total_attempted == 3, f"Expected 3 files attempted, got {total_attempted}"

    print("✅ Directory resilience test passed")


def run_all_tests():
    """Run all unit tests."""
    print("🧪 Running unit tests for raster_thumbnail package...\n")

    tests = [
        test_load_config,
        test_raster_type_detection,
        test_generate_thumbnail_invalid_input,
        test_process_directory_no_input,
        test_process_directory_no_files,
        test_process_directory_resilience,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1

    print("\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
