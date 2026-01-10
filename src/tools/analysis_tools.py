"""
Module responsible for running pylint on a Python file
and returning the analysis results.
"""

import os
import subprocess
from typing import Dict


from typing import Dict
import subprocess
import os

def run_pylint(file_path: str) -> Dict[str, float | str | int | bool]:
    """
    Run pylint on a Python file and extract the score.

    Args:
        file_path (str): Path to the Python file.

    Returns:
        dict: Dictionary containing pylint score and execution details.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    result = subprocess.run(
        ["pylint", file_path],
        capture_output=True,
        text=True,
        check=False
    )

   
    score = 0.0
    for line in result.stdout.split("\n"):
        if "rated at" in line:
            
            score = float(line.split("rated at")[1].split("/")[0].strip())

    return {
        "score": score,
        "max_score": 10.0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "success": result.returncode == 0
    }

def run_pytest(target_path: str) -> dict:
    """
    Run pytest on a given file or directory.

    Args:
        target_path (str): Path to test file or directory.

    Returns:
        dict: Dictionary containing passed, failed, stdout and stderr.
    """
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Path not found: {target_path}")

    result = subprocess.run(
        ["pytest", target_path, "--disable-warnings", "-q", "--tb=short"],
        capture_output=True,
        text=True,
        check=False
    )

    # Comptage des tests passés et échoués
    stdout = result.stdout
    passed = stdout.count("PASSED") if "PASSED" in stdout else 0
    failed = stdout.count("FAILED") if "FAILED" in stdout else 0

    return {
        "passed": passed,
        "failed": failed,
        "stdout": stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }

