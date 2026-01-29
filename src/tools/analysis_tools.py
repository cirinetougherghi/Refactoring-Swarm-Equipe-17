"""
Module responsible for running pylint on a Python file
and returning the analysis results.
"""

import os
import subprocess
from typing import Dict
from src.utils.logger import log_experiment, ActionType


def run_pylint(file_path: str) -> Dict[str, float | str | int | bool]:
    """
    Run pylint on a Python file and extract the score.

    Args:
        file_path (str): Path to the Python file.

    Returns:
        dict: Dictionary containing pylint score and execution details.
    """
    try:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        result = subprocess.run(
            ["pylint", file_path],
            capture_output=True,
            text=True,
            check=False,
            timeout=30
        )

        # Extract score
        score = 0.0
        for line in result.stdout.split("\n"):
            if "rated at" in line:
                score = float(line.split("rated at")[1].split("/")[0].strip())

        # Log successful execution
        log_experiment(
            agent_name="Pylint_Tool",
            model_used="pylint",
            action=ActionType.ANALYSIS,
            details={
                "operation": "static_analysis",
                "file_analyzed": file_path,
                "input_prompt": f"Analyzing code quality of: {file_path}",
                "output_response": f"Analysis complete. Score: {score}/10.0",
                "pylint_score": score,
                "max_score": 10.0,
                "returncode": result.returncode
            },
            status="SUCCESS"
        )

        return {
            "score": score,
            "max_score": 10.0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0
        }

    except FileNotFoundError as e:
        log_experiment(
            agent_name="Pylint_Tool",
            model_used="pylint",
            action=ActionType.DEBUG,
            details={
                "operation": "static_analysis",
                "file_analyzed": file_path,
                "input_prompt": f"Running pylint on: {file_path}",
                "output_response": f"File not found: {str(e)}",
                "error_type": "FileNotFoundError"
            },
            status="FAILURE"
        )
        raise

    except subprocess.TimeoutExpired:
        log_experiment(
            agent_name="Pylint_Tool",
            model_used="pylint",
            action=ActionType.DEBUG,
            details={
                "operation": "static_analysis",
                "file_analyzed": file_path,
                "input_prompt": f"Running pylint on: {file_path}",
                "output_response": "Pylint execution timeout after 30s",
                "error_type": "TimeoutExpired"
            },
            status="FAILURE"
        )
        raise

    except Exception as e:
        log_experiment(
            agent_name="Pylint_Tool",
            model_used="pylint",
            action=ActionType.DEBUG,
            details={
                "operation": "static_analysis",
                "file_analyzed": file_path,
                "input_prompt": f"Running pylint on: {file_path}",
                "output_response": f"Pylint failed: {str(e)}",
                "error_type": type(e).__name__
            },
            status="FAILURE"
        )
        raise


def run_pytest(target_path: str) -> dict:
    """
    Run pytest on a given file or directory.

    Args:
        target_path (str): Path to test file or directory.

    Returns:
        dict: Dictionary containing passed, failed, stdout and stderr.
    """
    try:
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Path not found: {target_path}")

        result = subprocess.run(
            ["pytest", target_path, "--disable-warnings", "-q", "--tb=short"],
            capture_output=True,
            text=True,
            check=False,
            timeout=60
        )

        # Comptage des tests passés et échoués
        stdout = result.stdout
        passed = stdout.count("PASSED") if "PASSED" in stdout else 0
        failed = stdout.count("FAILED") if "FAILED" in stdout else 0

        # Log execution
        log_experiment(
            agent_name="Pytest_Tool",
            model_used="pytest",
            action=ActionType.ANALYSIS if failed == 0 else ActionType.DEBUG,
            details={
                "operation": "unit_testing",
                "test_path": target_path,
                "input_prompt": f"Running tests in: {target_path}",
                "output_response": f"Tests completed: {passed} passed, {failed} failed",
                "passed_count": passed,
                "failed_count": failed,
                "returncode": result.returncode,
                "output_preview": stdout[:500]
            },
            status="SUCCESS" if failed == 0 else "FAILURE"
        )

        return {
            "passed": passed,
            "failed": failed,
            "stdout": stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

    except FileNotFoundError as e:
        log_experiment(
            agent_name="Pytest_Tool",
            model_used="pytest",
            action=ActionType.DEBUG,
            details={
                "operation": "unit_testing",
                "test_path": target_path,
                "input_prompt": f"Running tests in: {target_path}",
                "output_response": f"Path not found: {str(e)}",
                "error_type": "FileNotFoundError"
            },
            status="FAILURE"
        )
        raise

    except subprocess.TimeoutExpired:
        log_experiment(
            agent_name="Pytest_Tool",
            model_used="pytest",
            action=ActionType.DEBUG,
            details={
                "operation": "unit_testing",
                "test_path": target_path,
                "input_prompt": f"Running tests in: {target_path}",
                "output_response": "Pytest execution timeout after 60s",
                "error_type": "TimeoutExpired"
            },
            status="FAILURE"
        )
        raise

    except Exception as e:
        log_experiment(
            agent_name="Pytest_Tool",
            model_used="pytest",
            action=ActionType.DEBUG,
            details={
                "operation": "unit_testing",
                "test_path": target_path,
                "input_prompt": f"Running tests in: {target_path}",
                "output_response": f"Pytest failed: {str(e)}",
                "error_type": type(e).__name__
            },
            status="FAILURE"
        )
        raise