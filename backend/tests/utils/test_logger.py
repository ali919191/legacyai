"""
Test Logging Utility for Legacy AI Platform

This module provides a centralized logging mechanism for unit tests,
generating human-readable summaries in tests.log for monitoring AI system behavior.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union


class TestLogger:
    """
    Centralized test logging utility for the Legacy AI platform.

    This logger creates human-readable test summaries in tests.log,
    helping monitor AI system behavior and test results over time.
    """

    def __init__(self, log_file_path: Optional[str] = None):
        """
        Initialize the test logger.

        Args:
            log_file_path: Path to the log file. Defaults to tests.log in repository root.
        """
        if log_file_path is None:
            # Default to tests.log in repository root
            repo_root = self._find_repo_root()
            log_file_path = os.path.join(repo_root, "tests.log")

        self.log_file_path = log_file_path
        self._ensure_log_directory()

    def _find_repo_root(self) -> str:
        """Find the repository root directory."""
        current_dir = os.getcwd()
        while current_dir != os.path.dirname(current_dir):
            if os.path.exists(os.path.join(current_dir, ".git")):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        # Fallback to current directory if .git not found
        return os.getcwd()

    def _ensure_log_directory(self):
        """Ensure the log file directory exists."""
        log_dir = os.path.dirname(self.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def log_test_result(self,
                       test_name: str,
                       input_params: Dict[str, Any],
                       expected_result: Any,
                       actual_result: Any,
                       status: str,
                       additional_info: Optional[Dict[str, Any]] = None):
        """
        Log a test result to the test log file.

        Args:
            test_name: Name of the test method/class
            input_params: Dictionary of input parameters used in the test
            expected_result: Expected result of the test
            actual_result: Actual result obtained from the test
            status: PASS or FAIL
            additional_info: Optional additional information to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format input parameters for readability
        formatted_inputs = self._format_parameters(input_params)

        # Format results for readability
        formatted_expected = self._format_result(expected_result)
        formatted_actual = self._format_result(actual_result)

        # Create log entry
        log_entry = f"""
TEST: {test_name}
Timestamp: {timestamp}
Input: {formatted_inputs}
Expected: {formatted_expected}
Actual: {formatted_actual}
Status: {status}
"""

        if additional_info:
            log_entry += f"Additional Info: {json.dumps(additional_info, indent=2)}\n"

        log_entry += "---\n"

        # Append to log file
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def _format_parameters(self, params: Dict[str, Any]) -> str:
        """Format input parameters for human readability."""
        if not params:
            return "None"

        formatted = []
        for key, value in params.items():
            if isinstance(value, (list, tuple)):
                formatted.append(f"{key}={list(value)}")
            elif isinstance(value, dict):
                formatted.append(f"{key}={value}")
            else:
                formatted.append(f"{key}={repr(value)}")

        return ", ".join(formatted)

    def _format_result(self, result: Any) -> str:
        """Format test result for human readability."""
        if result is None:
            return "None"
        elif isinstance(result, (list, tuple)):
            return str(list(result))
        elif isinstance(result, dict):
            return json.dumps(result, indent=2)
        elif isinstance(result, bool):
            return str(result).upper()
        else:
            return str(result)

    def log_test_start(self, test_name: str, description: Optional[str] = None):
        """
        Log the start of a test suite or individual test.

        Args:
            test_name: Name of the test
            description: Optional description of what the test covers
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = f"""
=== STARTING TEST: {test_name} ===
Timestamp: {timestamp}
"""
        if description:
            log_entry += f"Description: {description}\n"

        log_entry += "\n"

        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def log_test_summary(self, test_name: str, total_tests: int, passed: int, failed: int):
        """
        Log a summary of test results.

        Args:
            test_name: Name of the test suite
            total_tests: Total number of tests run
            passed: Number of tests that passed
            failed: Number of tests that failed
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = f"""
=== TEST SUMMARY: {test_name} ===
Timestamp: {timestamp}
Total Tests: {total_tests}
Passed: {passed}
Failed: {failed}
Success Rate: {passed/total_tests*100:.1f}% if total_tests > 0 else 0
===

"""

        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)


# Global logger instance for easy access
test_logger = TestLogger()