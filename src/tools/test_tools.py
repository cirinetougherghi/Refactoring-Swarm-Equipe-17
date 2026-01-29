import subprocess
import json
import os
from src.utils.logger import log_experiment, ActionType


def run_pytest(target_dir="sandbox"):
    """
    Exécute pytest sur un répertoire donné et retourne les résultats au format JSON
    """
    try:
        # Vérifie si le répertoire existe
        if not os.path.exists(target_dir):
            raise FileNotFoundError(f"Le répertoire {target_dir} n'existe pas")

        # Lance pytest avec génération du rapport JSON
        result = subprocess.run(
            ["pytest", target_dir, "--json-report", "--json-report-file=report.json"],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Lit le rapport
        if os.path.exists("report.json"):
            with open("report.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {
                "error": "Le rapport JSON n'a pas été créé",
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        # Affiche le rapport pour débogage
        print("=== Rapport pytest ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # Log execution
        log_experiment(
            agent_name="Pytest_JSON_Tool",
            model_used="pytest",
            action=ActionType.ANALYSIS if result.returncode == 0 else ActionType.DEBUG,
            details={
                "operation": "pytest_with_json_report",
                "test_directory": target_dir,
                "input_prompt": f"Running pytest with JSON report on: {target_dir}",
                "output_response": f"Pytest completed with return code {result.returncode}",
                "returncode": result.returncode,
                "report_generated": os.path.exists("report.json"),
                "has_error": "error" in data
            },
            status="SUCCESS" if result.returncode == 0 and "error" not in data else "FAILURE"
        )

        return data

    except FileNotFoundError as e:
        log_experiment(
            agent_name="Pytest_JSON_Tool",
            model_used="pytest",
            action=ActionType.DEBUG,
            details={
                "operation": "pytest_with_json_report",
                "test_directory": target_dir,
                "input_prompt": f"Running pytest on: {target_dir}",
                "output_response": f"Directory not found: {str(e)}",
                "error_type": "FileNotFoundError"
            },
            status="FAILURE"
        )
        raise

    except subprocess.TimeoutExpired:
        log_experiment(
            agent_name="Pytest_JSON_Tool",
            model_used="pytest",
            action=ActionType.DEBUG,
            details={
                "operation": "pytest_with_json_report",
                "test_directory": target_dir,
                "input_prompt": f"Running pytest on: {target_dir}",
                "output_response": "Pytest execution timeout after 60s",
                "error_type": "TimeoutExpired"
            },
            status="FAILURE"
        )
        raise

    except Exception as e:
        log_experiment(
            agent_name="Pytest_JSON_Tool",
            model_used="pytest",
            action=ActionType.DEBUG,
            details={
                "operation": "pytest_with_json_report",
                "test_directory": target_dir,
                "input_prompt": f"Running pytest on: {target_dir}",
                "output_response": f"Pytest failed: {str(e)}",
                "error_type": type(e).__name__
            },
            status="FAILURE"
        )
        raise