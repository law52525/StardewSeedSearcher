#!/usr/bin/env python3
"""
Pytest runner script with various test configurations
Pytest运行脚本，支持多种测试配置
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return success status."""
    if description:
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"Command: {' '.join(cmd)}")
        print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def run_unit_tests():
    """Run unit tests only."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-m", "unit",
        "-v",
        "--tb=short",
        "--durations=10",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml"
    ]
    return run_command(cmd, "Unit Tests")


def run_integration_tests():
    """Run integration tests only."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-m", "integration",
        "-v",
        "--tb=short",
        "--durations=10",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml"
    ]
    return run_command(cmd, "Integration Tests")


def run_weather_tests():
    """Run weather predictor tests only."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_weather_predictor.py",
        "-v",
        "--tb=short",
        "--durations=10",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml"
    ]
    return run_command(cmd, "Weather Predictor Tests")


def run_validation_tests():
    """Run validation tests only."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_data_validation.py",
        "-v",
        "--tb=short",
        "--durations=10",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml"
    ]
    return run_command(cmd, "Validation Tests")


def run_websocket_tests():
    """Run WebSocket tests only."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_websocket_messages.py",
        "-v",
        "--tb=short",
        "--durations=10",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml"
    ]
    return run_command(cmd, "WebSocket Tests")


def run_consistency_tests():
    """Run consistency tests only."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_consistency.py",
        "-v",
        "--tb=short",
        "--durations=10",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml"
    ]
    return run_command(cmd, "Consistency Tests")


def run_benchmark_tests():
    """Run benchmark tests only."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_benchmark.py",
        "-v",
        "--tb=short",
        "--benchmark-only",
        "--benchmark-sort=mean",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml"
    ]
    return run_command(cmd, "Benchmark Tests")


def run_gpu_tests():
    """Run GPU acceleration tests only."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_gpu_acceleration.py",
        "-v",
        "--tb=short",
        "--durations=10",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml"
    ]
    return run_command(cmd, "GPU Tests")


def run_all_tests():
    """Run all tests."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--durations=10",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--html=reports/pytest_report.html",
        "--self-contained-html"
    ]
    return run_command(cmd, "All Tests")


def run_tests_with_coverage():
    """Run tests with coverage report."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--html=reports/pytest_report.html",
        "--self-contained-html"
    ]
    return run_command(cmd, "Tests with Coverage")


def run_parallel_tests():
    """Run tests in parallel."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-n", "auto",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--html=reports/pytest_report.html",
        "--self-contained-html"
    ]
    return run_command(cmd, "Parallel Tests")


def run_fast_tests():
    """Run fast tests only (exclude slow and benchmark tests)."""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-m", "not slow and not benchmark",
        "--durations=10",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml"
    ]
    return run_command(cmd, "Fast Tests")


def run_specific_test(test_path):
    """Run a specific test file or test function."""
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-v",
        "--tb=short",
        "--durations=10",
        "--cov=internal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml"
    ]
    return run_command(cmd, f"Specific Test: {test_path}")


def main():
    """Main function to run tests based on command line arguments."""
    parser = argparse.ArgumentParser(description="Run pytest tests with various configurations")
    parser.add_argument(
        "test_type",
        choices=[
            "unit", "integration", "weather", "validation", "websocket",
            "consistency", "benchmark", "gpu", "all", "coverage", "parallel", "fast"
        ],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--test-path",
        help="Specific test file or function to run"
    )
    parser.add_argument(
        "--create-reports-dir",
        action="store_true",
        help="Create reports directory if it doesn't exist"
    )
    
    args = parser.parse_args()
    
    # Create reports directory if requested
    if args.create_reports_dir:
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        print(f"Created reports directory: {reports_dir.absolute()}")
    
    # Run specific test if path provided
    if args.test_path:
        success = run_specific_test(args.test_path)
    else:
        # Run tests based on type
        test_functions = {
            "unit": run_unit_tests,
            "integration": run_integration_tests,
            "weather": run_weather_tests,
            "validation": run_validation_tests,
            "websocket": run_websocket_tests,
            "consistency": run_consistency_tests,
            "benchmark": run_benchmark_tests,
            "gpu": run_gpu_tests,
            "all": run_all_tests,
            "coverage": run_tests_with_coverage,
            "parallel": run_parallel_tests,
            "fast": run_fast_tests,
        }
        
        test_function = test_functions.get(args.test_type)
        if test_function:
            success = test_function()
        else:
            print(f"Unknown test type: {args.test_type}")
            return 1
    
    # Print result
    if success:
        print(f"\n{'='*60}")
        print("[SUCCESS] All tests passed successfully!")
        print(f"{'='*60}")
        return 0
    else:
        print(f"\n{'='*60}")
        print("[FAILURE] Some tests failed!")
        print(f"{'='*60}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
